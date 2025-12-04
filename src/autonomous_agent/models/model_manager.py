"""
Model management for autonomous research agent.
Handles loading, managing, and interfacing with different LLM backends.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import requests

from ..config import ModelConfig, get_config

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """Base class for all model implementations."""
    
    def __init__(self, config: ModelConfig):
        """
        Initialize the model.
        
        Args:
            config: Model configuration
        """
        self.config = config
        self.loaded = False
    
    @abstractmethod
    def load(self) -> None:
        """Load the model into memory."""
        pass
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Generate text from the model.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional model-specific parameters
            
        Returns:
            Generated text
        """
        pass
    
    def unload(self) -> None:
        """Unload the model from memory."""
        self.loaded = False


class OllamaModel(BaseModel):
    """Ollama model implementation."""
    
    def __init__(self, config: ModelConfig):
        """Initialize Ollama model."""
        super().__init__(config)
        self.base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    def load(self) -> None:
        """Load is a no-op for Ollama (models are loaded on-demand)."""
        logger.info(f"Ollama model {self.config.name} ready (loaded on-demand)")
        self.loaded = True
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Generate text using Ollama API.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        endpoint = f"{self.base_url}/api/generate"
        
        # Prepare request payload
        payload = {
            "model": self.config.model_path,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens or self.config.max_tokens,
                "temperature": temperature or self.config.temperature,
                "top_p": self.config.top_p,
            }
        }
        
        try:
            logger.info(f"Generating with Ollama model: {self.config.name}")
            response = requests.post(endpoint, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {e}")
            raise Exception(f"Failed to generate response from Ollama: {e}")


class LocalTransformersModel(BaseModel):
    """Local HuggingFace Transformers model implementation."""
    
    def __init__(self, config: ModelConfig):
        """Initialize local transformers model."""
        super().__init__(config)
        self.model = None
        self.tokenizer = None
    
    def load(self) -> None:
        """Load the model and tokenizer."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            logger.info(f"Loading local model: {self.config.model_path}")
            
            # Determine device
            if self.config.device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                device = self.config.device
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=True
            )
            
            # Load model with quantization if specified
            load_kwargs = {
                "pretrained_model_name_or_path": self.config.model_path,
                "trust_remote_code": True
            }
            
            if self.config.quantization == "4bit":
                from transformers import BitsAndBytesConfig
                load_kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16
                )
            elif self.config.quantization == "8bit":
                load_kwargs["load_in_8bit"] = True
            else:
                load_kwargs["torch_dtype"] = torch.float16
                load_kwargs["device_map"] = device
            
            self.model = AutoModelForCausalLM.from_pretrained(**load_kwargs)
            
            self.loaded = True
            logger.info(f"Model {self.config.name} loaded successfully on {device}")
        
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Generate text using local model.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        if not self.loaded or self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        try:
            logger.info(f"Generating with local model: {self.config.name}")
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # Move to same device as model
            if hasattr(self.model, "device"):
                inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            # Generate
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens or self.config.max_tokens,
                temperature=temperature or self.config.temperature,
                top_p=self.config.top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                **kwargs
            )
            
            # Decode
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the prompt from the generated text
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
        
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
    
    def unload(self) -> None:
        """Unload the model from memory."""
        if self.model is not None:
            del self.model
            self.model = None
        
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        
        # Clear CUDA cache if available
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        
        self.loaded = False
        logger.info(f"Model {self.config.name} unloaded")


class ModelManager:
    """
    Manages multiple language models and handles model selection and generation.
    """
    
    def __init__(self, config: Optional[Any] = None):
        """
        Initialize the model manager.
        
        Args:
            config: Optional configuration object
        """
        self.config = config or get_config()
        self.configs: Dict[str, ModelConfig] = self.config.models.copy()
        self.models: Dict[str, BaseModel] = {}
        
        logger.info(f"ModelManager initialized with {len(self.configs)} model configs")
    
    def register_model(self, name: str, config: ModelConfig) -> None:
        """
        Register a new model configuration.
        
        Args:
            name: Model identifier
            config: Model configuration
        """
        self.configs[name] = config
        logger.info(f"Registered model: {name}")
    
    def load_model(self, name: str) -> None:
        """
        Load a specific model.
        
        Args:
            name: Model identifier
        """
        if name not in self.configs:
            raise ValueError(f"Model {name} not found in configurations")
        
        if name in self.models:
            logger.info(f"Model {name} already loaded")
            return
        
        config = self.configs[name]
        
        # Create appropriate model instance
        if config.model_type == "ollama":
            model = OllamaModel(config)
        elif config.model_type == "local":
            model = LocalTransformersModel(config)
        else:
            raise ValueError(f"Unsupported model type: {config.model_type}")
        
        # Load the model
        model.load()
        self.models[name] = model
        
        logger.info(f"Model {name} loaded and ready")
    
    def unload_model(self, name: str) -> None:
        """
        Unload a specific model.
        
        Args:
            name: Model identifier
        """
        if name in self.models:
            self.models[name].unload()
            del self.models[name]
            logger.info(f"Model {name} unloaded")
    
    def generate(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using a specified model.
        
        Args:
            prompt: Input prompt
            model_name: Model to use (defaults to configured default)
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        # Use default model if not specified
        if model_name is None:
            model_name = self.config.agent.default_model
        
        # Load model if not already loaded
        if model_name not in self.models:
            self.load_model(model_name)
        
        # Generate
        return self.models[model_name].generate(prompt, **kwargs)
    
    def select_best_model(self, task_type: str) -> str:
        """
        Select the best model for a given task type.
        
        Args:
            task_type: Type of task (code, reasoning, general, fast, creative)
            
        Returns:
            Model name
        """
        # Heuristic-based model selection
        task_to_model = {
            "code": "llama",
            "reasoning": "llama",
            "general": "mistral",
            "fast": "phi",
            "creative": "mistral",
        }
        
        selected = task_to_model.get(task_type, "mistral")
        
        # Fallback to first available model if selected not in configs
        if selected not in self.configs:
            selected = list(self.configs.keys())[0] if self.configs else "llama"
        
        logger.info(f"Selected model '{selected}' for task type '{task_type}'")
        return selected
    
    def list_models(self) -> List[str]:
        """
        List all registered model names.
        
        Returns:
            List of model names
        """
        return list(self.configs.keys())
    
    def list_loaded_models(self) -> List[str]:
        """
        List currently loaded model names.
        
        Returns:
            List of loaded model names
        """
        return list(self.models.keys())
    
    def unload_all(self) -> None:
        """Unload all loaded models."""
        for name in list(self.models.keys()):
            self.unload_model(name)
        
        logger.info("All models unloaded")
