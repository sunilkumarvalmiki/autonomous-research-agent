# Running the Autonomous Research Agent

This guide shows you how to run the autonomous research agent successfully.

## Quick Start - Agent is Ready! ✅

The agent can now be initialized and run successfully. The core infrastructure is in place:

```bash
# Run the demo to verify the agent works
python demo_agent.py
```

This will show:
- ✓ Agent initialization
- ✓ Available models (llama, mistral, phi)
- ✓ Model selection capabilities
- ✓ Agent features and statistics

## What's Working

The agent now has:

1. **Complete Model Management** (`src/autonomous_agent/models/model_manager.py`)
   - `ModelManager` - Orchestrates multiple LLMs
   - `OllamaModel` - Connects to Ollama for easy local inference
   - `LocalTransformersModel` - Supports HuggingFace models with quantization

2. **Research Agent** (`src/autonomous_agent/agents/research_agent.py`)
   - Single-step research queries
   - Multi-step reasoning (breaks complex queries into sub-questions)
   - Automatic model selection based on task type
   - Feedback collection for self-improvement
   - Statistics tracking

3. **Configuration System** (`src/autonomous_agent/config.py`)
   - Flexible model configuration
   - RAG settings
   - Agent behavior customization

4. **CLI Interface** (`src/autonomous_agent/cli.py`)
   - `research` - Ask research questions
   - `stats` - View agent statistics
   - `add-knowledge` - Add documents to knowledge base
   - `config` - Manage configuration

## Running with Full Inference

To actually query LLMs and get responses, you need to set up a model backend:

### Option 1: Ollama (Recommended - Easiest)

```bash
# 1. Install Ollama
# Visit https://ollama.ai/ or:
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Start Ollama service
ollama serve

# 3. Pull a model (in another terminal)
ollama pull llama3.1:8b

# 4. Run the simple example
python examples/simple_research.py
```

### Option 2: Local Models (Requires GPU)

```bash
# 1. Install all dependencies
pip install -r requirements.txt

# 2. Create a custom config with local model
cat > config.json << EOF
{
  "models": {
    "local-llama": {
      "name": "llama-2-7b",
      "model_type": "local",
      "model_path": "meta-llama/Llama-2-7b-chat-hf",
      "quantization": "4bit",
      "device": "auto"
    }
  }
}
EOF

# 3. Run with config
python -c "
from autonomous_agent import ResearchAgent
from autonomous_agent.config import Config, set_config

config = Config.load('config.json')
config.agent.enable_rag = False
set_config(config)

agent = ResearchAgent()
result = agent.research('What is AI?', model_name='local-llama')
print(result['response'])
"
```

## Using the Python API

```python
from autonomous_agent import ResearchAgent
from autonomous_agent.config import Config, set_config

# Disable RAG if you don't have sentence-transformers installed
config = Config.load_default()
config.agent.enable_rag = False
set_config(config)

# Initialize agent
agent = ResearchAgent()

# Simple research (requires Ollama to be running)
result = agent.research("What are the benefits of open-source AI?")
print(result['response'])

# Multi-step research
result = agent.multi_step_research(
    "How can I build a production-ready AI application?",
    max_steps=3
)
print(result['final_answer'])

# Add feedback for self-improvement
agent.add_feedback(
    query="What are the benefits of open-source AI?",
    response=result['response'],
    rating=4,
    comments="Good comprehensive answer"
)

# View statistics
stats = agent.get_statistics()
print(f"Total interactions: {stats['total_interactions']}")
print(f"Average rating: {stats['average_rating']}")
```

## Using the CLI

```bash
# Install the package
pip install -e .

# Research a question (requires Ollama)
autonomous-agent research "What is quantum computing?"

# Multi-step research
autonomous-agent research "Explain machine learning" --multi-step --steps 3

# View statistics
autonomous-agent stats

# Show configuration
autonomous-agent config --show

# Create default config
autonomous-agent config --init --output my-config.json
```

## Examples

The `examples/` directory contains ready-to-run examples:

1. **simple_research.py** - Basic research query
2. **rag_example.py** - Using knowledge base with RAG
3. **multi_step_research.py** - Complex multi-step reasoning

## Tests

All model manager tests pass:

```bash
# Run tests
PYTHONPATH=src python -m pytest tests/test_model_manager.py -v

# Results: 10 passed
```

## Architecture

```
src/autonomous_agent/
├── __init__.py              # Package entry point
├── models/                  # ✅ Model management (NEW)
│   ├── __init__.py
│   └── model_manager.py    # ModelManager, OllamaModel, LocalTransformersModel
├── agents/                  # Research agent implementation
│   ├── __init__.py
│   └── research_agent.py   # Main agent logic
├── rag/                     # RAG knowledge base
│   ├── __init__.py
│   └── knowledge_base.py
├── config.py                # Configuration management
├── cli.py                   # Command-line interface
└── api.py                   # REST API (optional)
```

## Troubleshooting

### "Connection refused" or Ollama errors
Make sure Ollama is running: `ollama serve`

### "No module named 'sentence_transformers'"
Either install it with `pip install sentence-transformers` or disable RAG:
```python
config.agent.enable_rag = False
```

### "Model not found"
Pull the model first: `ollama pull llama3.1:8b`

## Next Steps

1. **Install Ollama** for easy local inference
2. **Run examples** in the `examples/` directory
3. **Try the CLI** for quick research queries
4. **Add knowledge** to the knowledge base for domain-specific expertise
5. **Customize models** by editing the configuration

The autonomous research agent is now fully functional and ready to use! 🚀
