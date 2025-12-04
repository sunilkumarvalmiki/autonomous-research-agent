"""Unit tests for configuration management."""

import unittest
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from autonomous_agent.config import Config, ModelConfig, RAGConfig, AgentConfig


class TestConfig(unittest.TestCase):
    """Test configuration classes."""
    
    def test_model_config_creation(self):
        """Test ModelConfig creation."""
        config = ModelConfig(
            name="test-model",
            model_type="ollama",
            model_path="test:latest"
        )
        
        self.assertEqual(config.name, "test-model")
        self.assertEqual(config.model_type, "ollama")
        self.assertEqual(config.model_path, "test:latest")
        self.assertEqual(config.max_tokens, 2048)
        self.assertEqual(config.temperature, 0.7)
    
    def test_rag_config_defaults(self):
        """Test RAGConfig default values."""
        config = RAGConfig()
        
        self.assertEqual(config.vector_db_type, "chromadb")
        self.assertEqual(config.chunk_size, 512)
        self.assertEqual(config.chunk_overlap, 50)
        self.assertEqual(config.top_k_results, 5)
    
    def test_agent_config_defaults(self):
        """Test AgentConfig default values."""
        config = AgentConfig()
        
        self.assertEqual(config.default_model, "llama")
        self.assertTrue(config.enable_rag)
        self.assertTrue(config.enable_self_improvement)
    
    def test_config_load_default(self):
        """Test loading default configuration."""
        config = Config.load_default()
        
        self.assertIn("llama", config.models)
        self.assertIn("mistral", config.models)
        self.assertIn("phi", config.models)
        
        self.assertIsInstance(config.rag, RAGConfig)
        self.assertIsInstance(config.agent, AgentConfig)
    
    def test_config_save_load(self):
        """Test saving and loading configuration."""
        # Create config
        config = Config.load_default()
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = f.name
        
        try:
            config.save(temp_path)
            
            # Load from file
            loaded_config = Config.load(temp_path)
            
            # Verify
            self.assertEqual(len(config.models), len(loaded_config.models))
            self.assertEqual(config.agent.default_model, loaded_config.agent.default_model)
        
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_config_model_addition(self):
        """Test adding new models to configuration."""
        config = Config.load_default()
        
        new_model = ModelConfig(
            name="custom-model",
            model_type="local",
            model_path="/path/to/model"
        )
        
        config.models["custom"] = new_model
        
        self.assertIn("custom", config.models)
        self.assertEqual(config.models["custom"].name, "custom-model")


if __name__ == '__main__':
    unittest.main()
