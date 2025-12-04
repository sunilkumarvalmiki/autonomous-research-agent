"""Unit tests for model manager (mocking actual model loading)."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path for direct test execution (when not installed via pip)
_src_path = str(Path(__file__).parent.parent / 'src')
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)

from autonomous_agent.models.model_manager import ModelManager, OllamaModel, LocalTransformersModel
from autonomous_agent.config import ModelConfig


class TestModelManager(unittest.TestCase):
    """Test ModelManager functionality."""
    
    def test_model_manager_initialization(self):
        """Test initializing model manager."""
        manager = ModelManager()
        
        self.assertIsInstance(manager, ModelManager)
        self.assertGreater(len(manager.configs), 0)
    
    def test_register_model(self):
        """Test registering a new model."""
        manager = ModelManager()
        
        config = ModelConfig(
            name="test-model",
            model_type="ollama",
            model_path="test:latest"
        )
        
        manager.register_model("test", config)
        
        self.assertIn("test", manager.configs)
        self.assertEqual(manager.configs["test"].name, "test-model")
    
    def test_list_models(self):
        """Test listing registered models."""
        manager = ModelManager()
        
        models = manager.list_models()
        
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)
    
    def test_select_best_model(self):
        """Test model selection heuristics."""
        manager = ModelManager()
        
        # Test different task types
        self.assertEqual(manager.select_best_model("code"), "llama")
        self.assertEqual(manager.select_best_model("reasoning"), "llama")
        self.assertEqual(manager.select_best_model("general"), "mistral")
        self.assertEqual(manager.select_best_model("fast"), "phi")


class TestOllamaModel(unittest.TestCase):
    """Test OllamaModel functionality."""
    
    def test_ollama_model_creation(self):
        """Test creating Ollama model instance."""
        config = ModelConfig(
            name="test",
            model_type="ollama",
            model_path="llama3.1:8b"
        )
        
        model = OllamaModel(config)
        
        self.assertEqual(model.config, config)
        self.assertIn("localhost", model.base_url)
    
    def test_ollama_load(self):
        """Test Ollama load (should be no-op)."""
        config = ModelConfig(
            name="test",
            model_type="ollama",
            model_path="llama3.1:8b"
        )
        
        model = OllamaModel(config)
        model.load()  # Should not raise
    
    @patch('requests.post')
    def test_ollama_generate_success(self, mock_post):
        """Test Ollama generation with mocked response."""
        config = ModelConfig(
            name="test",
            model_type="ollama",
            model_path="test:latest"
        )
        
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"response": "Generated text"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        model = OllamaModel(config)
        result = model.generate("Test prompt")
        
        self.assertEqual(result, "Generated text")
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_ollama_generate_error(self, mock_post):
        """Test Ollama generation with error."""
        config = ModelConfig(
            name="test",
            model_type="ollama",
            model_path="test:latest"
        )
        
        # Mock error response
        mock_post.side_effect = Exception("Connection error")
        
        model = OllamaModel(config)
        
        with self.assertRaises(Exception):
            model.generate("Test prompt")


class TestLocalTransformersModel(unittest.TestCase):
    """Test LocalTransformersModel functionality."""
    
    def test_local_model_creation(self):
        """Test creating local model instance."""
        config = ModelConfig(
            name="test",
            model_type="local",
            model_path="meta-llama/Llama-2-7b"
        )
        
        model = LocalTransformersModel(config)
        
        self.assertEqual(model.config, config)
        self.assertIsNone(model.model)
        self.assertIsNone(model.tokenizer)
    
    def test_generate_without_load(self):
        """Test that generate raises error if model not loaded."""
        config = ModelConfig(
            name="test",
            model_type="local",
            model_path="test"
        )
        
        model = LocalTransformersModel(config)
        
        with self.assertRaises(RuntimeError):
            model.generate("Test")


if __name__ == '__main__':
    unittest.main()
