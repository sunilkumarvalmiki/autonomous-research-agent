#!/usr/bin/env python3
"""
Command-line interface for the autonomous research agent.
"""

import argparse
import sys
import json
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from autonomous_agent import ResearchAgent
from autonomous_agent.config import Config, set_config
from autonomous_agent.utils.text_utils import chunk_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cmd_research(args):
    """Execute research command."""
    logger.info(f"Researching: {args.query}")
    
    # Load config if provided
    if args.config:
        config = Config.load(args.config)
        set_config(config)
    
    # Initialize agent
    agent = ResearchAgent()
    
    # Perform research
    if args.multi_step:
        result = agent.multi_step_research(args.query, max_steps=args.steps)
        output = {
            "query": result["query"],
            "sub_questions": result["sub_questions"],
            "final_answer": result["final_answer"],
            "steps_taken": result["steps_taken"]
        }
    else:
        result = agent.research(args.query, use_rag=args.use_rag, model_name=args.model)
        output = {
            "query": result["query"],
            "response": result["response"],
            "model": result["model"]
        }
    
    # Output result
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        if args.json:
            print(json.dumps(output, indent=2))
        else:
            print("\n" + "=" * 60)
            print("QUERY:", output.get("query"))
            print("=" * 60)
            if "final_answer" in output:
                print("\nFINAL ANSWER:")
                print(output["final_answer"])
                print("\n" + "-" * 60)
                print("SUB-QUESTIONS:")
                for i, sq in enumerate(output["sub_questions"], 1):
                    print(f"  {i}. {sq}")
            else:
                print("\nRESPONSE:")
                print(output["response"])
            print("=" * 60 + "\n")


def cmd_add_knowledge(args):
    """Add knowledge to the knowledge base."""
    logger.info(f"Adding knowledge from: {args.file}")
    
    # Load config if provided
    if args.config:
        config = Config.load(args.config)
        set_config(config)
    
    # Initialize agent
    agent = ResearchAgent()
    
    # Read file
    with open(args.file, 'r') as f:
        content = f.read()
    
    # Chunk if needed
    if args.chunk:
        chunks = chunk_text(content, chunk_size=args.chunk_size, overlap=args.overlap)
    else:
        chunks = [content]
    
    # Add to knowledge base
    metadata = {"source": args.file}
    if args.metadata:
        metadata.update(json.loads(args.metadata))
    
    for chunk in chunks:
        agent.add_to_knowledge_base(chunk, metadata)
    
    print(f"Added {len(chunks)} document(s) to knowledge base")


def cmd_stats(args):
    """Show agent statistics."""
    logger.info("Retrieving agent statistics")
    
    # Load config if provided
    if args.config:
        config = Config.load(args.config)
        set_config(config)
    
    # Initialize agent
    agent = ResearchAgent()
    
    # Get statistics
    stats = agent.get_statistics()
    
    print("\n" + "=" * 60)
    print("AGENT STATISTICS")
    print("=" * 60)
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n{key.upper()}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")
    print("=" * 60 + "\n")


def cmd_config(args):
    """Manage configuration."""
    if args.init:
        # Create default configuration
        config = Config.load_default()
        output_file = args.output or "config.json"
        config.save(output_file)
        print(f"Default configuration saved to {output_file}")
    
    elif args.show:
        # Show configuration
        if args.file:
            config = Config.load(args.file)
        else:
            config = Config.load_default()
        
        print(json.dumps(config.model_dump(), indent=2))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous Research Agent - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Research command
    research_parser = subparsers.add_parser('research', help='Perform research on a query')
    research_parser.add_argument('query', help='Research query')
    research_parser.add_argument('--model', '-m', help='Specific model to use')
    research_parser.add_argument('--use-rag', action='store_true', help='Use RAG for context')
    research_parser.add_argument('--multi-step', action='store_true', help='Use multi-step research')
    research_parser.add_argument('--steps', type=int, default=3, help='Number of steps for multi-step research')
    research_parser.add_argument('--config', '-c', help='Path to config file')
    research_parser.add_argument('--output', '-o', help='Output file for results (JSON)')
    research_parser.add_argument('--json', action='store_true', help='Output as JSON to stdout')
    research_parser.set_defaults(func=cmd_research)
    
    # Add knowledge command
    knowledge_parser = subparsers.add_parser('add-knowledge', help='Add knowledge to the knowledge base')
    knowledge_parser.add_argument('file', help='File containing knowledge to add')
    knowledge_parser.add_argument('--chunk', action='store_true', help='Chunk the document')
    knowledge_parser.add_argument('--chunk-size', type=int, default=512, help='Chunk size')
    knowledge_parser.add_argument('--overlap', type=int, default=50, help='Chunk overlap')
    knowledge_parser.add_argument('--metadata', help='JSON metadata for the document')
    knowledge_parser.add_argument('--config', '-c', help='Path to config file')
    knowledge_parser.set_defaults(func=cmd_add_knowledge)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show agent statistics')
    stats_parser.add_argument('--config', '-c', help='Path to config file')
    stats_parser.set_defaults(func=cmd_stats)
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument('--init', action='store_true', help='Create default configuration')
    config_parser.add_argument('--show', action='store_true', help='Show configuration')
    config_parser.add_argument('--file', '-f', help='Config file to show')
    config_parser.add_argument('--output', '-o', help='Output file for init')
    config_parser.set_defaults(func=cmd_config)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    try:
        args.func(args)
        return 0
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
