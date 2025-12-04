# Example Configuration File

This is an example configuration file for the Autonomous Research Agent.
Copy this file and modify it according to your needs.

## Usage

```bash
# Save as config.json
cp config.example.json config.json

# Use with CLI
autonomous-agent research "query" --config config.json

# Use with API
# Set CONFIG_FILE environment variable
export CONFIG_FILE=config.json
python -m autonomous_agent.api
```

## Configuration Structure

```json
{
  "models": {
    "llama": {
      "name": "llama-3.1-8b",
      "model_type": "ollama",
      "model_path": "llama3.1:8b",
      "api_endpoint": "",
      "max_tokens": 2048,
      "temperature": 0.7,
      "top_p": 0.9,
      "quantization": "",
      "device": "auto"
    },
    "mistral": {
      "name": "mistral-7b",
      "model_type": "ollama",
      "model_path": "mistral:7b",
      "max_tokens": 2048,
      "temperature": 0.7,
      "top_p": 0.9,
      "quantization": "",
      "device": "auto"
    },
    "phi": {
      "name": "phi-3",
      "model_type": "ollama",
      "model_path": "phi3:medium",
      "max_tokens": 2048,
      "temperature": 0.7,
      "top_p": 0.9,
      "quantization": "",
      "device": "auto"
    }
  },
  "rag": {
    "vector_db_type": "chromadb",
    "vector_db_path": "./data/vector_db",
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "chunk_size": 512,
    "chunk_overlap": 50,
    "top_k_results": 5,
    "similarity_threshold": 0.7
  },
  "agent": {
    "default_model": "llama",
    "enable_rag": true,
    "enable_self_improvement": true,
    "max_iterations": 10,
    "feedback_storage_path": "./data/feedback",
    "log_level": "INFO"
  }
}
```

## Model Configuration Options

### model_type
- `ollama`: Use Ollama for model serving (easiest)
- `local`: Use HuggingFace Transformers locally
- `api`: Use external API endpoint

### quantization
- `""` (empty): No quantization
- `"4bit"`: 4-bit quantization (for local models)
- `"8bit"`: 8-bit quantization (for local models)

### device
- `"auto"`: Automatically select device
- `"cuda"`: Use NVIDIA GPU
- `"cpu"`: Use CPU only
- `"mps"`: Use Apple Silicon GPU (M1/M2)

## RAG Configuration Options

### vector_db_type
- `"chromadb"`: ChromaDB (recommended, persistent)
- `"faiss"`: FAISS (fast, in-memory with save/load)

### embedding_model
Popular options:
- `"sentence-transformers/all-MiniLM-L6-v2"`: Fast, good quality
- `"sentence-transformers/all-mpnet-base-v2"`: Better quality, slower
- `"BAAI/bge-small-en-v1.5"`: Very good quality

## Advanced Configuration Examples

### Local HuggingFace Model
```json
{
  "custom_local": {
    "name": "custom-llama",
    "model_type": "local",
    "model_path": "meta-llama/Llama-2-7b-chat-hf",
    "max_tokens": 2048,
    "temperature": 0.7,
    "quantization": "4bit",
    "device": "cuda"
  }
}
```

### Custom Ollama Endpoint
```json
{
  "remote_ollama": {
    "name": "remote-llama",
    "model_type": "ollama",
    "model_path": "llama3.1:8b",
    "api_endpoint": "http://192.168.1.100:11434",
    "max_tokens": 2048,
    "temperature": 0.7
  }
}
```

### FAISS Configuration
```json
{
  "rag": {
    "vector_db_type": "faiss",
    "vector_db_path": "./data/faiss_index",
    "embedding_model": "BAAI/bge-small-en-v1.5",
    "chunk_size": 1024,
    "chunk_overlap": 100,
    "top_k_results": 10
  }
}
```

## Environment-Specific Configurations

### Development
```json
{
  "agent": {
    "default_model": "phi",
    "enable_rag": true,
    "log_level": "DEBUG"
  }
}
```

### Production
```json
{
  "agent": {
    "default_model": "llama",
    "enable_rag": true,
    "enable_self_improvement": true,
    "log_level": "INFO"
  }
}
```

### Resource-Constrained
```json
{
  "models": {
    "phi": {
      "model_path": "phi3:mini",
      "max_tokens": 1024
    }
  },
  "rag": {
    "chunk_size": 256,
    "top_k_results": 3
  }
}
```
