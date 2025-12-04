"""
Configuration management for the autonomous research agent.
"""

import os
from typing import Dict, Any, List
from pathlib import Path
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Configuration for individual models."""
    name: str
    model_type: str  # 'local', 'api', 'ollama'
    model_path: str = ""
    api_endpoint: str = ""
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    quantization: str = ""  # '4bit', '8bit', 'none'
    device: str = "auto"


class RAGConfig(BaseModel):
    """Configuration for RAG system."""
    vector_db_type: str = "chromadb"  # 'chromadb', 'faiss'
    vector_db_path: str = "./data/vector_db"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k_results: int = 5
    similarity_threshold: float = 0.7


class AgentConfig(BaseModel):
    """Configuration for the research agent."""
    default_model: str = "llama"
    enable_rag: bool = True
    enable_self_improvement: bool = True
    max_iterations: int = 10
    feedback_storage_path: str = "./data/feedback"
    log_level: str = "INFO"


class Config(BaseModel):
    """Main configuration class."""
    models: Dict[str, ModelConfig] = Field(default_factory=dict)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    
    @classmethod
    def load_default(cls) -> "Config":
        """Load default configuration with common open-source models."""
        return cls(
            models={
                "llama": ModelConfig(
                    name="llama-3.1-8b",
                    model_type="ollama",
                    model_path="llama3.1:8b",
                    max_tokens=2048,
                    temperature=0.7
                ),
                "mistral": ModelConfig(
                    name="mistral-7b",
                    model_type="ollama",
                    model_path="mistral:7b",
                    max_tokens=2048,
                    temperature=0.7
                ),
                "phi": ModelConfig(
                    name="phi-3",
                    model_type="ollama",
                    model_path="phi3:medium",
                    max_tokens=2048,
                    temperature=0.7
                ),
            },
            rag=RAGConfig(),
            agent=AgentConfig()
        )
    
    def save(self, path: str) -> None:
        """Save configuration to JSON file."""
        with open(path, 'w') as f:
            f.write(self.model_dump_json(indent=2))
    
    @classmethod
    def load(cls, path: str) -> "Config":
        """Load configuration from JSON file."""
        with open(path, 'r') as f:
            return cls.model_validate_json(f.read())


# Global config instance
_config: Config = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load_default()
    return _config


def set_config(config: Config) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
