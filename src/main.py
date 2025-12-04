"""
Main orchestrator for the autonomous research agent with production-grade enhancements.
"""

import sys
import logging
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential

from scraper import DataScraper
from analyzer import ResearchAnalyzer
from formatter import OutputFormatter
from github_api import GitHubAPI
from observability import ObservabilityManager, PerformanceMonitor, MetricType, calculate_quality_score
from memory import AgentMemory
from evaluation import ResearchEvaluator

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
    """Main entry point for the research agent with production-grade features."""
    parser = argparse.ArgumentParser(description='Autonomous Research Agent (Production Grade)')
    parser.add_argument('--query', required=True, help='Research query/topic')
    parser.add_argument('--issue-body', default='', help='Issue body for configuration')
    parser.add_argument('--repo', help='GitHub repository (owner/name)')
    parser.add_argument('--issue-number', type=int, help='GitHub issue number')
    parser.add_argument('--output-dir', default='./outputs', help='Output directory')
    parser.add_argument('--enable-memory', action='store_true', default=True, help='Enable memory and learning')
    parser.add_argument('--enable-evaluation', action='store_true', default=True, help='Enable quality evaluation')
    
    args = parser.parse_args()
    
    # Initialize observability
    obs_manager = ObservabilityManager()
    
    logger.info(f"Starting research on: {args.query}")
    logger.info("🚀 Production-grade features enabled: Observability, Memory, Evaluation")
    
    with PerformanceMonitor(obs_manager, "full_research_workflow"):
        try:
            # Parse configuration
            config = parse_issue_config(args.issue_body)
            logger.info(f"Configuration: {config}")
            
            # Initialize components
            with PerformanceMonitor(obs_manager, "component_initialization"):
                scraper = DataScraper()
                analyzer = ResearchAnalyzer()
                formatter = OutputFormatter()
                github_api = GitHubAPI()
                memory = AgentMemory(enable_vector_memory=args.enable_memory, enable_cache=args.enable_memory)
                evaluator = ResearchEvaluator() if args.enable_evaluation else None
            
            # Check memory for similar past research
            if memory.vector_memory:
                past_context = memory.get_context_from_memory(args.query)
                if past_context:
                    logger.info("📚 Found relevant past research in memory")
            
            # Step 1: Scrape data with retry logic
            logger.info("Step 1: Scraping data sources...")
            with PerformanceMonitor(obs_manager, "data_scraping"):
                data = scrape_with_retry(scraper, args.query, config)
            
            total_items = sum(len(v) for v in data.values())
            logger.info(f"Scraped {total_items} total items")
            
            # Record data quality metric
            quality_score = calculate_quality_score(data)
            obs_manager.record_metric(MetricType.DATA_QUALITY, quality_score, {"query": args.query})
            
            if total_items == 0:
                logger.warning("No data found for query")
                obs_manager.record_metric(MetricType.TASK_COMPLETION, 0.0)
                if args.repo and args.issue_number:
                    github_api.post_comment(
                        args.repo,
                        args.issue_number,
                        f"⚠️ No research data found for query: '{args.query}'\n\nPlease try a different search term or adjust the configuration."
                    )
                sys.exit(1)
            
            # Step 2: Analyze with LLM
            logger.info("Step 2: Analyzing data with LLM...")
            with PerformanceMonitor(obs_manager, "llm_analysis"):
                analysis = analyzer.analyze(data, args.query)
            logger.info("Analysis completed")
            
            # Step 3: Generate outputs
            logger.info("Step 3: Generating output formats...")
            with PerformanceMonitor(obs_manager, "output_generation"):
                outputs = formatter.generate_all(args.query, data, analysis)
            logger.info(f"Generated {len(outputs)} output formats")
            
            # Step 4: Evaluate quality
            evaluation_report = None
            if evaluator:
                logger.info("Step 4: Evaluating research quality...")
                with PerformanceMonitor(obs_manager, "quality_evaluation"):
                    evaluation_report = evaluator.comprehensive_evaluation(
                        args.query, data, analysis, outputs
                    )
                
                logger.info(f"📊 Quality Score: {evaluation_report['overall_score']} - {evaluation_report['rating']}")
                obs_manager.record_metric(
                    MetricType.ACCURACY,
                    evaluation_report['overall_score'],
                    {"rating": evaluation_report['rating']}
                )
                
                # Self-improvement: Log recommendations
                if evaluation_report['recommendations']:
                    logger.info("💡 Recommendations for improvement:")
                    for rec in evaluation_report['recommendations']:
                        logger.info(f"  - {rec}")
            
            # Step 5: Store in memory for learning
            if memory:
                logger.info("Step 5: Storing research in memory...")
                with PerformanceMonitor(obs_manager, "memory_storage"):
                    memory.remember_research(args.query, data, analysis)
            
            # Step 6: Save outputs
            logger.info("Step 6: Saving outputs...")
            output_path = Path(args.output_dir)
            save_outputs(outputs, output_path)
            
            # Save evaluation report if available
            if evaluation_report:
                import json
                eval_path = output_path / "evaluation_report.json"
                with open(eval_path, 'w') as f:
                    json.dump(evaluation_report, f, indent=2)
                logger.info(f"Saved evaluation report to {eval_path}")
            
            # Save observability metrics
            metrics_path = output_path / "metrics.json"
            obs_manager.export_metrics(str(metrics_path))
            
            # Also save to docs/index.html for GitHub Pages
            docs_path = Path('docs')
            docs_path.mkdir(exist_ok=True)
            with open(docs_path / 'index.html', 'w', encoding='utf-8') as f:
                f.write(outputs['html'])
            logger.info("Saved HTML dashboard to docs/index.html")
            
            # Step 7: Post to GitHub issue
            if args.repo and args.issue_number:
                logger.info("Step 7: Posting results to GitHub issue...")
                
                # Enhanced summary with quality metrics
                summary_comment = create_enhanced_summary(
                    github_api,
                    outputs,
                    evaluation_report,
                    obs_manager
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
            
            # Record successful completion
            obs_manager.record_metric(MetricType.TASK_COMPLETION, 1.0)
            
            # Print final summary
            summary = obs_manager.get_summary()
            logger.info(f"""
✅ Research completed successfully!

📊 Performance Summary:
- Total Duration: {summary['session_duration']:.2f}s
- Success Rate: {summary['success_rate']:.1%}
- Data Quality: {quality_score}
- Overall Quality: {evaluation_report['overall_score'] if evaluation_report else 'N/A'}
- Quality Rating: {evaluation_report['rating'] if evaluation_report else 'N/A'}
""")
            
        except Exception as e:
            logger.error(f"Error during research: {e}", exc_info=True)
            obs_manager.record_error("research_failure", str(e))
            obs_manager.record_metric(MetricType.ERROR_RATE, 1.0)
            
            if args.repo and args.issue_number:
                github_api.post_comment(
                    args.repo,
                    args.issue_number,
                    f"❌ Research failed with error:\n\n```\n{str(e)}\n```\n\nPlease check the workflow logs for details."
                )
            
            sys.exit(1)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def scrape_with_retry(scraper: DataScraper, query: str, config: Dict[str, str]) -> Dict[str, Any]:
    """Scrape data with automatic retry on failure."""
    return scraper.scrape_all(
        query=query,
        focus=config.get('focus', 'all'),
        time_range=config.get('time_range', 'month'),
        depth=config.get('depth', 'standard')
    )


def create_enhanced_summary(github_api: GitHubAPI, outputs: Dict[str, str], 
                           evaluation_report: Dict[str, Any], 
                           obs_manager: ObservabilityManager) -> str:
    """Create enhanced summary with quality metrics."""
    base_comment = github_api.create_summary_comment(
        outputs['markdown'],
        outputs['mermaid']
    )
    
    # Add quality metrics if available
    if evaluation_report:
        quality_section = f"""

## 📊 Quality Metrics

- **Overall Score**: {evaluation_report['overall_score']} / 1.0
- **Quality Rating**: {evaluation_report['rating']}
- **Comprehensiveness**: {evaluation_report['scores']['comprehensiveness']}
- **Relevance**: {evaluation_report['scores']['relevance']}
- **Analysis Quality**: {evaluation_report['scores']['analysis_quality']}

### Recommendations
"""
        for rec in evaluation_report['recommendations']:
            quality_section += f"- {rec}\n"
        
        base_comment += quality_section
    
    # Add performance metrics
    summary = obs_manager.get_summary()
    perf_section = f"""

## ⚡ Performance

- **Total Duration**: {summary['session_duration']:.2f}s
- **Success Rate**: {summary['success_rate']:.0%}
- **Operations Completed**: {summary['completed_traces']}
"""
    
    base_comment += perf_section
    
    return base_comment


if __name__ == '__main__':
    main()
