"""
Main orchestrator for the autonomous research agent.
"""

import os
import sys
import logging
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any

from scraper import DataScraper
from analyzer import ResearchAnalyzer
from formatter import OutputFormatter
from github_api import GitHubAPI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_issue_config(issue_body: str) -> Dict[str, str]:
    """Parse configuration from issue body YAML front matter."""
    default_config = {
        'depth': 'standard',
        'focus': 'all',
        'time_range': 'month'
    }
    
    if not issue_body:
        return default_config
    
    # Check for YAML front matter
    if issue_body.strip().startswith('---'):
        parts = issue_body.split('---', 2)
        if len(parts) >= 3:
            try:
                config = yaml.safe_load(parts[1])
                if isinstance(config, dict):
                    default_config.update(config)
                    logger.info(f"Parsed config from issue: {config}")
            except yaml.YAMLError as e:
                logger.warning(f"Failed to parse YAML config: {e}")
    
    return default_config


def extract_query_from_title(title: str) -> str:
    """Extract research query from issue title."""
    # Remove common prefixes
    for prefix in ['Research:', 'research:', 'Research -', 'research -']:
        if title.startswith(prefix):
            return title[len(prefix):].strip()
    return title.strip()


def save_outputs(outputs: Dict[str, str], output_dir: Path):
    """Save all output formats to files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    file_extensions = {
        'markdown': 'md',
        'json': 'json',
        'html': 'html',
        'bibtex': 'bib',
        'csv': 'csv',
        'mermaid': 'mmd'
    }
    
    for format_name, content in outputs.items():
        ext = file_extensions.get(format_name, 'txt')
        file_path = output_dir / f"research_report.{ext}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Saved {format_name} output to {file_path}")


def main():
    """Main entry point for the research agent."""
    parser = argparse.ArgumentParser(description='Autonomous Research Agent')
    parser.add_argument('--query', required=True, help='Research query/topic')
    parser.add_argument('--issue-body', default='', help='Issue body for configuration')
    parser.add_argument('--repo', help='GitHub repository (owner/name)')
    parser.add_argument('--issue-number', type=int, help='GitHub issue number')
    parser.add_argument('--output-dir', default='./outputs', help='Output directory')
    
    args = parser.parse_args()
    
    logger.info(f"Starting research on: {args.query}")
    
    # Parse configuration
    config = parse_issue_config(args.issue_body)
    logger.info(f"Configuration: {config}")
    
    # Initialize components
    scraper = DataScraper()
    analyzer = ResearchAnalyzer()
    formatter = OutputFormatter()
    github_api = GitHubAPI()
    
    try:
        # Step 1: Scrape data
        logger.info("Step 1: Scraping data sources...")
        data = scraper.scrape_all(
            query=args.query,
            focus=config.get('focus', 'all'),
            time_range=config.get('time_range', 'month'),
            depth=config.get('depth', 'standard')
        )
        
        total_items = sum(len(v) for v in data.values())
        logger.info(f"Scraped {total_items} total items")
        
        if total_items == 0:
            logger.warning("No data found for query")
            if args.repo and args.issue_number:
                github_api.post_comment(
                    args.repo,
                    args.issue_number,
                    f"⚠️ No research data found for query: '{args.query}'\n\nPlease try a different search term or adjust the configuration."
                )
            sys.exit(1)
        
        # Step 2: Analyze with LLM
        logger.info("Step 2: Analyzing data with LLM...")
        analysis = analyzer.analyze(data, args.query)
        logger.info("Analysis completed")
        
        # Step 3: Generate outputs
        logger.info("Step 3: Generating output formats...")
        outputs = formatter.generate_all(args.query, data, analysis)
        logger.info(f"Generated {len(outputs)} output formats")
        
        # Step 4: Save outputs
        logger.info("Step 4: Saving outputs...")
        output_path = Path(args.output_dir)
        save_outputs(outputs, output_path)
        
        # Also save to docs/index.html for GitHub Pages
        docs_path = Path('docs')
        docs_path.mkdir(exist_ok=True)
        with open(docs_path / 'index.html', 'w', encoding='utf-8') as f:
            f.write(outputs['html'])
        logger.info("Saved HTML dashboard to docs/index.html")
        
        # Step 5: Post to GitHub issue
        if args.repo and args.issue_number:
            logger.info("Step 5: Posting results to GitHub issue...")
            summary_comment = github_api.create_summary_comment(
                outputs['markdown'],
                outputs['mermaid']
            )
            
            success = github_api.post_comment(
                args.repo,
                args.issue_number,
                summary_comment
            )
            
            if success:
                github_api.add_label(args.repo, args.issue_number, 'completed')
                logger.info("Successfully posted results to issue")
            else:
                logger.warning("Failed to post results to issue")
        
        logger.info("✅ Research completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during research: {e}", exc_info=True)
        
        if args.repo and args.issue_number:
            github_api.post_comment(
                args.repo,
                args.issue_number,
                f"❌ Research failed with error:\n\n```\n{str(e)}\n```\n\nPlease check the workflow logs for details."
            )
        
        sys.exit(1)


if __name__ == '__main__':
    main()
