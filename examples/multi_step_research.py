#!/usr/bin/env python3
"""
Example demonstrating multi-step research capabilities.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from autonomous_agent import ResearchAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run multi-step research example."""
    print("=" * 60)
    print("Autonomous Research Agent - Multi-Step Research")
    print("=" * 60)
    
    # Initialize agent
    print("\n1. Initializing agent...")
    agent = ResearchAgent()
    
    # Complex research query
    query = "How can I build a self-improving AI agent using open-source models?"
    
    print(f"\n2. Complex research query:\n   {query}")
    
    # Perform multi-step research
    print("\n3. Performing multi-step research...")
    print("   (Breaking down into sub-questions and researching each)")
    
    result = agent.multi_step_research(query, max_steps=3)
    
    print("\n4. Research breakdown:")
    print("-" * 60)
    print("Sub-questions identified:")
    for i, sq in enumerate(result['sub_questions'], 1):
        print(f"   {i}. {sq}")
    
    print("\n5. Sub-question answers:")
    print("-" * 60)
    for i, sr in enumerate(result['sub_results'], 1):
        print(f"\nQ{i}: {sr['question']}")
        print(f"A{i}: {sr['answer'][:200]}...")  # Truncate for display
    
    print("\n6. Synthesized final answer:")
    print("-" * 60)
    print(result['final_answer'])
    print("-" * 60)
    
    print(f"\n7. Research completed in {result['steps_taken']} steps")
    
    print("\n" + "=" * 60)
    print("Multi-step research completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error running multi-step example: {e}", exc_info=True)
        sys.exit(1)
