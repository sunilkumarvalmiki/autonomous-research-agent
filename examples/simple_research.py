#!/usr/bin/env python3
"""
Simple example demonstrating the autonomous research agent.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from autonomous_agent import ResearchAgent, ModelManager, KnowledgeBase
from autonomous_agent.config import Config, get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run a simple research example."""
    print("=" * 60)
    print("Autonomous Research Agent - Simple Example")
    print("=" * 60)
    
    # Initialize agent
    print("\n1. Initializing agent...")
    agent = ResearchAgent()
    
    # Example research query
    query = "What are the benefits of using open-source language models?"
    
    print(f"\n2. Research query: {query}")
    
    # Perform research (without RAG for this simple example)
    print("\n3. Generating response...")
    result = agent.research(query, use_rag=False)
    
    print("\n4. Results:")
    print("-" * 60)
    print(f"Model used: {result['model']}")
    print(f"Response:\n{result['response']}")
    print("-" * 60)
    
    # Add feedback
    print("\n5. Recording feedback...")
    agent.add_feedback(
        query=query,
        response=result['response'],
        rating=4,
        comments="Good response, covered main points"
    )
    
    # Show statistics
    print("\n6. Agent statistics:")
    stats = agent.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error running example: {e}", exc_info=True)
        sys.exit(1)
