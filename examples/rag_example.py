#!/usr/bin/env python3
"""
Example demonstrating RAG (Retrieval-Augmented Generation) capabilities.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from autonomous_agent import ResearchAgent
from autonomous_agent.utils.text_utils import chunk_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Sample knowledge to add to the knowledge base
SAMPLE_KNOWLEDGE = """
Open-source language models have revolutionized AI accessibility. Models like LLaMA, 
Mistral, and Gemma provide powerful capabilities without vendor lock-in. These models 
can be deployed locally, ensuring data privacy and control.

Key advantages of open-source LLMs include:
1. Transparency: You can inspect the model architecture and training data
2. Customization: Fine-tune models for specific domains
3. Cost-effectiveness: No API fees for inference
4. Privacy: Keep sensitive data in-house
5. Community support: Active development and improvements

Self-improvement mechanisms for AI agents include:
1. RAG (Retrieval-Augmented Generation): Enhance responses with retrieved information
2. Fine-tuning: Adapt models to specific tasks using LoRA or QLoRA
3. Feedback loops: Learn from user interactions
4. Knowledge base updates: Continuously expand the information repository
5. Multi-model ensembles: Combine strengths of different models
"""


def main():
    """Run RAG example."""
    print("=" * 60)
    print("Autonomous Research Agent - RAG Example")
    print("=" * 60)
    
    # Initialize agent with RAG enabled
    print("\n1. Initializing agent with RAG...")
    agent = ResearchAgent()
    
    # Add knowledge to the knowledge base
    print("\n2. Adding knowledge to the knowledge base...")
    chunks = chunk_text(SAMPLE_KNOWLEDGE, chunk_size=300, overlap=50)
    
    for i, chunk in enumerate(chunks, 1):
        agent.add_to_knowledge_base(
            chunk,
            metadata={"source": "introduction", "chunk_id": i}
        )
    
    print(f"   Added {len(chunks)} chunks to knowledge base")
    
    # Research with RAG
    query = "How can AI agents improve themselves?"
    
    print(f"\n3. Research query with RAG: {query}")
    print("\n4. Generating response...")
    
    result = agent.research(query, use_rag=True)
    
    print("\n5. Results:")
    print("-" * 60)
    print(f"Model used: {result['model']}")
    print(f"Retrieved documents: {result['retrieved_documents']}")
    print(f"Response:\n{result['response']}")
    print("-" * 60)
    
    # Try another query
    query2 = "What are the advantages of open-source LLMs?"
    print(f"\n6. Second query: {query2}")
    
    result2 = agent.research(query2, use_rag=True)
    
    print("\n7. Results:")
    print("-" * 60)
    print(f"Model used: {result2['model']}")
    print(f"Retrieved documents: {result2['retrieved_documents']}")
    print(f"Response:\n{result2['response']}")
    print("-" * 60)
    
    # Show statistics
    print("\n8. Final statistics:")
    stats = agent.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print("RAG example completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error running RAG example: {e}", exc_info=True)
        sys.exit(1)
