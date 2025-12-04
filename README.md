# Autonomous Research Agent

An intelligent research agent leveraging open-source language models with self-improvement capabilities through RAG (Retrieval-Augmented Generation), multi-model support, and continuous learning mechanisms.

## 🌟 Features

- **Multi-Model Support**: Seamlessly work with multiple open-source LLMs (Llama, Mistral, Phi, Gemma)
- **RAG Integration**: Enhanced responses using vector-based knowledge retrieval
- **Self-Improvement**: Learn from feedback and continuously improve performance
- **Multi-Step Reasoning**: Break down complex queries into manageable sub-tasks
- **Flexible Deployment**: Support for local models (via Ollama) and HuggingFace Transformers
- **Evaluation Metrics**: Built-in metrics to assess response quality
- **Knowledge Base Management**: Store and retrieve domain-specific information

## 📋 Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) (optional, for easy local model deployment)
- CUDA-capable GPU (optional, for local transformer models)

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sunilkumarvalmiki/autonomous-research-agent.git
cd autonomous-research-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install Ollama and pull a model:
```bash
# Install Ollama from https://ollama.ai/
ollama pull llama3.1:8b
ollama pull mistral:7b
```

### Basic Usage

```python
from autonomous_agent import ResearchAgent

# Initialize the agent
agent = ResearchAgent()

# Perform research
result = agent.research("What are the benefits of open-source AI models?")

print(result['response'])

# Add feedback for self-improvement
agent.add_feedback(
    query="What are the benefits of open-source AI models?",
    response=result['response'],
    rating=5,
    comments="Excellent comprehensive answer"
)
```

### Run Examples

```bash
# Simple research example
python examples/simple_research.py

# RAG (Retrieval-Augmented Generation) example
python examples/rag_example.py

# Multi-step research example
python examples/multi_step_research.py
```

## 📖 Documentation

### Architecture

The system consists of several key components:

1. **Model Manager**: Handles loading and managing multiple LLMs
2. **Knowledge Base**: Vector database for RAG functionality
3. **Research Agent**: Main agent orchestrating research tasks
4. **Evaluation System**: Metrics for assessing response quality

```
┌─────────────────────────────────────────────────────────────┐
│                    Autonomous Research Agent                 │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Query       │→ │   Planning   │→ │   Execution     │  │
│  │   Analyzer    │  │   Module     │  │   Engine        │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
│          ↓                  ↓                   ↓            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Model Selection & Routing                │  │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐     │  │
│  │  │ Llama  │  │Mistral │  │ Gemma  │  │  Phi   │     │  │
│  │  └────────┘  └────────┘  └────────┘  └────────┘     │  │
│  └───────────────────────────────────────────────────────┘  │
│          ↓                  ↓                   ↓            │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Knowledge   │  │  Evaluation  │  │  Self-Learning  │  │
│  │   Base (RAG)  │  │  & Metrics   │  │  Module         │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Configuration

Customize the agent by modifying the configuration:

```python
from autonomous_agent.config import Config, ModelConfig

# Create custom configuration
config = Config.load_default()

# Add a custom model
config.models['custom'] = ModelConfig(
    name="custom-model",
    model_type="ollama",
    model_path="custom:latest",
    max_tokens=4096,
    temperature=0.8
)

# Update RAG settings
config.rag.chunk_size = 1024
config.rag.top_k_results = 10

# Save configuration
config.save("config.json")
```

### RAG (Retrieval-Augmented Generation)

Add knowledge to enhance responses:

```python
from autonomous_agent import ResearchAgent
from autonomous_agent.utils.text_utils import chunk_text

agent = ResearchAgent()

# Add documents to knowledge base
document = "Your domain-specific knowledge here..."
chunks = chunk_text(document, chunk_size=512)

for chunk in chunks:
    agent.add_to_knowledge_base(chunk, metadata={"source": "manual"})

# Research with RAG
result = agent.research("Query related to your knowledge", use_rag=True)
```

### Multi-Step Research

For complex queries requiring decomposition:

```python
agent = ResearchAgent()

result = agent.multi_step_research(
    "How can I build a production-ready AI application?",
    max_steps=5
)

print(result['final_answer'])
```

## 🔬 Research Background

See [RESEARCH.md](RESEARCH.md) for comprehensive research on:
- Open-source LLM landscape
- Self-improvement mechanisms
- RAG implementation strategies
- Fine-tuning techniques (LoRA, QLoRA)
- Model evaluation frameworks

## 🛠️ Advanced Features

### Custom Model Integration

```python
from autonomous_agent.models.model_manager import ModelManager, ModelConfig

# Configure a local HuggingFace model
model_config = ModelConfig(
    name="local-llama",
    model_type="local",
    model_path="meta-llama/Llama-2-7b-chat-hf",
    quantization="4bit",
    device="auto"
)

manager = ModelManager()
manager.register_model("local-llama", model_config)
manager.load_model("local-llama")
```

### Feedback-Driven Improvement

```python
# Collect feedback
agent.add_feedback(
    query="...",
    response="...",
    rating=3,
    comments="Could be more detailed"
)

# View statistics
stats = agent.get_statistics()
print(f"Average rating: {stats['average_rating']}")
print(f"Total interactions: {stats['total_interactions']}")
```

## 📊 Supported Models

| Model | Size | Type | Best For |
|-------|------|------|----------|
| Llama 3.1 | 8B, 70B, 405B | General | Reasoning, Code |
| Mistral | 7B | General | Speed, Quality |
| Phi-3 | 3.8B | Small | Edge devices |
| Gemma | 2B, 7B | Lightweight | Resource-constrained |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Ollama](https://ollama.ai/)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers/)
- [ChromaDB](https://www.trychroma.com/)

## 🙏 Acknowledgments

Built with open-source models and frameworks:
- Meta's LLaMA
- Mistral AI
- HuggingFace
- LangChain ecosystem
- ChromaDB

---

**Note**: This project requires either Ollama installed locally or access to HuggingFace models. For best results, use models with at least 7B parameters.