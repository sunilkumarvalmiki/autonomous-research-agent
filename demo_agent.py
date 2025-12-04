#!/usr/bin/env python3
"""
Demo script showing the autonomous research agent running.
This demonstrates that the agent can be initialized and used.

This demo runs without requiring Ollama or sentence-transformers to be installed,
showing the agent's structure and capabilities.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from autonomous_agent.config import Config, set_config
from autonomous_agent import ResearchAgent


def demo_agent_initialization():
    """Demonstrate that the agent can be initialized."""
    print("=" * 60)
    print("Autonomous Research Agent - Demo")
    print("=" * 60)
    
    print("\n1. Loading configuration...")
    config = Config.load_default()
    config.agent.enable_rag = False  # Disable RAG for demo (requires sentence-transformers)
    set_config(config)
    print("   ✓ Configuration loaded")
    print(f"   ✓ RAG enabled: {config.agent.enable_rag}")
    print(f"   ✓ Self-improvement enabled: {config.agent.enable_self_improvement}")
    
    print("\n2. Initializing ResearchAgent...")
    agent = ResearchAgent()
    print("   ✓ Agent initialized successfully")
    print(f"   ✓ Default model: {config.agent.default_model}")
    
    print("\n3. Available models:")
    for model_name in agent.model_manager.list_models():
        model_config = agent.model_manager.configs[model_name]
        print(f"   - {model_name}: {model_config.name} ({model_config.model_type})")
    
    print("\n4. Model selection capabilities:")
    print("   The agent automatically selects the best model based on task type:")
    task_types = ["code", "reasoning", "general", "fast", "creative"]
    for task in task_types:
        selected = agent.model_manager.select_best_model(task)
        print(f"   - {task:12} → {selected}")
    
    print("\n5. Agent capabilities:")
    print("   ✓ Single-step research queries")
    print("   ✓ Multi-step reasoning (breaks complex queries into sub-questions)")
    print("   ✓ Automatic model selection based on task type")
    print("   ✓ Feedback collection for self-improvement")
    print("   ✓ Statistics tracking")
    print("   ✓ RAG integration (when enabled with required dependencies)")
    print("   ✓ CLI interface for command-line usage")
    print("   ✓ Python API for programmatic access")
    
    print("\n6. Current statistics:")
    stats = agent.get_statistics()
    print(f"   - Total interactions: {stats['total_interactions']}")
    print(f"   - Average rating: {stats['average_rating']}")
    print(f"   - Knowledge base documents: {stats['knowledge_base_documents']}")
    print(f"   - Loaded models: {len(stats['loaded_models'])} (loaded on-demand)")
    
    print("\n7. Example usage:")
    print("   Python API:")
    print("   ```python")
    print("   from autonomous_agent import ResearchAgent")
    print("   agent = ResearchAgent()")
    print("   result = agent.research('What is quantum computing?')")
    print("   print(result['response'])")
    print("   ```")
    
    print("\n   CLI:")
    print("   ```bash")
    print("   autonomous-agent research 'What is quantum computing?'")
    print("   autonomous-agent stats")
    print("   autonomous-agent config --show")
    print("   ```")
    
    print("\n" + "=" * 60)
    print("✅ Agent Setup Complete!")
    print("=" * 60)
    
    print("\n📝 To run the agent with actual model inference:")
    print("\n   Option 1: Using Ollama (Recommended - Easy Setup)")
    print("   1. Install Ollama from https://ollama.ai/")
    print("   2. Start Ollama service: ollama serve")
    print("   3. Pull a model: ollama pull llama3.1:8b")
    print("   4. Run example: python examples/simple_research.py")
    
    print("\n   Option 2: Using Local Models (Requires GPU)")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Configure local model in config.json")
    print("   3. Run with custom config")
    
    print("\n📦 Installation:")
    print("   pip install -e .")
    
    print("\n🚀 The autonomous research agent is ready to run!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        demo_agent_initialization()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
