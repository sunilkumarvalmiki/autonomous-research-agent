# Autonomous Research Agent - Getting Started

## Installation Guide

### Prerequisites

1. **Python 3.8 or higher**
   ```bash
   python --version  # Should be 3.8+
   ```

2. **Ollama (Recommended for easiest setup)**
   - Visit [ollama.ai](https://ollama.ai/) and download for your platform
   - Or install via command line:
     ```bash
     # macOS
     brew install ollama
     
     # Linux
     curl -fsSL https://ollama.ai/install.sh | sh
     ```

3. **GPU (Optional but recommended)**
   - NVIDIA GPU with CUDA support for local transformer models
   - Ollama works well on CPU too

### Step-by-Step Setup

#### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/sunilkumarvalmiki/autonomous-research-agent.git
cd autonomous-research-agent

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install in development mode
pip install -e .
```

#### 2. Set Up Ollama Models

```bash
# Start Ollama service (if not auto-started)
ollama serve

# In another terminal, pull models
ollama pull llama3.1:8b     # Recommended: Good all-rounder (4.7GB)
ollama pull mistral:7b      # Alternative: Fast and efficient (4.1GB)
ollama pull phi3:medium     # Lightweight option (7.9GB)

# Verify models are installed
ollama list
```

#### 3. Run Your First Example

```bash
# Simple research example
python examples/simple_research.py

# If you get import errors, make sure you're in the project root
# and the virtual environment is activated
```

## Quick Start Examples

### Example 1: Basic Research

```python
from autonomous_agent import ResearchAgent

# Initialize
agent = ResearchAgent()

# Ask a question
result = agent.research("Explain quantum computing in simple terms")

# Print answer
print(result['response'])
```

### Example 2: With Knowledge Base (RAG)

```python
from autonomous_agent import ResearchAgent

agent = ResearchAgent()

# Add your own knowledge
agent.add_to_knowledge_base(
    "Quantum computers use qubits that can be in superposition...",
    metadata={"topic": "quantum", "source": "physics_book"}
)

# Research with your knowledge
result = agent.research("What are qubits?", use_rag=True)
print(result['response'])
```

### Example 3: Multi-Step Complex Research

```python
from autonomous_agent import ResearchAgent

agent = ResearchAgent()

# Complex query that needs breakdown
result = agent.multi_step_research(
    "How do I deploy a machine learning model to production?",
    max_steps=4
)

# See the breakdown
for i, sub in enumerate(result['sub_questions'], 1):
    print(f"{i}. {sub}")

# See final synthesized answer
print("\nFinal Answer:")
print(result['final_answer'])
```

## Configuration

### Using Different Models

```python
from autonomous_agent import ResearchAgent

agent = ResearchAgent()

# Use a specific model
result = agent.research(
    "Write a Python function to sort a list",
    model_name="mistral"  # or "llama", "phi"
)
```

### Custom Configuration

Create a `config.json` file:

```json
{
  "models": {
    "llama": {
      "name": "llama-3.1-8b",
      "model_type": "ollama",
      "model_path": "llama3.1:8b",
      "max_tokens": 2048,
      "temperature": 0.7
    }
  },
  "rag": {
    "vector_db_type": "chromadb",
    "chunk_size": 512,
    "top_k_results": 5
  },
  "agent": {
    "default_model": "llama",
    "enable_rag": true,
    "enable_self_improvement": true
  }
}
```

Load it:

```python
from autonomous_agent.config import Config, set_config

config = Config.load("config.json")
set_config(config)

agent = ResearchAgent()  # Will use your config
```

## Troubleshooting

### Issue: "Connection refused" or Ollama errors

**Solution**: Make sure Ollama is running:
```bash
ollama serve
```

### Issue: Import errors

**Solution**: 
1. Ensure you're in the project root directory
2. Activate virtual environment
3. Verify installation: `pip list | grep langchain`

### Issue: Out of memory

**Solution**:
1. Use smaller models (phi3:medium)
2. Close other applications
3. Use quantized models (4-bit versions)

### Issue: Slow responses

**Solution**:
1. Use faster models (mistral:7b)
2. Reduce max_tokens in config
3. Consider GPU acceleration

## Next Steps

1. **Read the Research Document**: See [RESEARCH.md](RESEARCH.md) for in-depth information
2. **Try the Examples**: Run all examples in the `examples/` folder
3. **Customize**: Modify configuration for your use case
4. **Add Knowledge**: Build your domain-specific knowledge base
5. **Experiment**: Try different models and parameters

## Common Use Cases

### Use Case 1: Domain Expert Assistant

```python
agent = ResearchAgent()

# Add domain knowledge
with open("medical_papers.txt") as f:
    agent.add_to_knowledge_base(f.read(), metadata={"domain": "medical"})

# Ask domain-specific questions
result = agent.research("What are the latest treatments for diabetes?", use_rag=True)
```

### Use Case 2: Code Assistant

```python
agent = ResearchAgent()

# Use code-optimized model
result = agent.research(
    "Write a FastAPI endpoint for user authentication",
    model_name="llama"  # Llama is good at code
)

print(result['response'])
```

### Use Case 3: Research Synthesizer

```python
agent = ResearchAgent()

result = agent.multi_step_research(
    "Compare different approaches to handling concurrency in Python",
    max_steps=3
)

# Get comprehensive comparison
print(result['final_answer'])
```

## Getting Help

- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the code docstrings for detailed API info

## Performance Tips

1. **Model Selection**:
   - General queries: Mistral or Llama
   - Code: Llama
   - Fast responses: Phi-3
   - Creative: Mistral

2. **RAG Optimization**:
   - Chunk size: 512-1024 tokens
   - Overlap: 50-100 tokens
   - Top K: 3-5 documents

3. **Memory Management**:
   - Load models on-demand
   - Use quantized versions
   - Unload unused models

Happy researching! 🚀
