"""
Formatter module for generating multi-format outputs.
Supports Markdown, JSON, HTML, BibTeX, CSV, and Mermaid diagrams.
"""

import json
import csv
import io
import logging
from typing import Dict, List, Any
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarkdownFormatter:
    """Generate comprehensive Markdown reports."""
    
    def format(self, query: str, data: Dict[str, List[Dict[str, Any]]], analysis: Dict[str, Any]) -> str:
        """Generate Markdown report."""
        md = []
        
        # Header
        md.append(f"# Research Report: {query}")
        md.append(f"\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        # Executive Summary
        md.append("## Executive Summary\n")
        md.append(analysis.get('summary', 'No summary available.'))
        md.append("\n")
        
        # Key Findings
        if analysis.get('key_findings'):
            md.append("## Key Findings\n")
            for i, finding in enumerate(analysis['key_findings'], 1):
                md.append(f"{i}. {finding}")
            md.append("\n")
        
        # Trends and Patterns
        if analysis.get('trends'):
            md.append("## Trends and Patterns\n")
            md.append(str(analysis['trends']))
            md.append("\n")
        
        # Academic Papers
        if data.get('papers'):
            md.append(f"## Academic Papers ({len(data['papers'])} found)\n")
            for i, paper in enumerate(data['papers'][:10], 1):
                md.append(f"### {i}. {paper.get('title', 'N/A')}\n")
                md.append(f"**Authors:** {', '.join(paper.get('authors', [])[:5])}\n")
                md.append(f"**Published:** {paper.get('published', 'N/A')}\n")
                md.append(f"**Link:** [{paper.get('link', '')}]({paper.get('link', '')})\n")
                md.append(f"**Summary:** {paper.get('summary', '')[:300]}...\n")
                md.append(f"**Categories:** {', '.join(paper.get('categories', [])[:3])}\n")
        
        # GitHub Repositories
        if data.get('repositories'):
            md.append(f"\n## GitHub Repositories ({len(data['repositories'])} found)\n")
            for i, repo in enumerate(data['repositories'][:10], 1):
                md.append(f"### {i}. [{repo.get('title', 'N/A')}]({repo.get('url', '')})\n")
                md.append(f"**Stars:** ⭐ {repo.get('stars', 0)} | **Language:** {repo.get('language', 'N/A')}\n")
                md.append(f"**Description:** {repo.get('description', 'No description available.')}\n")
        
        # News & Articles
        if data.get('news'):
            md.append(f"\n## News & Articles ({len(data['news'])} found)\n")
            for i, article in enumerate(data['news'][:10], 1):
                md.append(f"{i}. [{article.get('title', 'N/A')}]({article.get('url', '')})")
                if article.get('score'):
                    md.append(f" (Score: {article['score']})")
                md.append(f" - *{article.get('source', 'Unknown')}*\n")
        
        # Discussions
        if data.get('discussions'):
            md.append(f"\n## Community Discussions ({len(data['discussions'])} found)\n")
            for i, disc in enumerate(data['discussions'][:10], 1):
                md.append(f"{i}. [{disc.get('title', 'N/A')}]({disc.get('url', '')})")
                md.append(f" - r/{disc.get('subreddit', 'unknown')} ({disc.get('score', 0)} points)\n")
        
        # Recommendations
        if analysis.get('recommendations'):
            md.append("\n## Recommendations\n")
            for i, rec in enumerate(analysis['recommendations'], 1):
                md.append(f"{i}. {rec}")
            md.append("\n")
        
        # Statistics
        md.append("\n## Statistics\n")
        md.append(f"- Total Papers: {len(data.get('papers', []))}")
        md.append(f"- Total Repositories: {len(data.get('repositories', []))}")
        md.append(f"- Total News Articles: {len(data.get('news', []))}")
        md.append(f"- Total Discussions: {len(data.get('discussions', []))}")
        
        return "\n".join(md)


class JSONFormatter:
    """Generate structured JSON output."""
    
    def format(self, query: str, data: Dict[str, List[Dict[str, Any]]], analysis: Dict[str, Any]) -> str:
        """Generate JSON report."""
        output = {
            "query": query,
            "generated_at": datetime.now().isoformat(),
            "analysis": analysis,
            "data": data,
            "statistics": {
                "total_papers": len(data.get('papers', [])),
                "total_repositories": len(data.get('repositories', [])),
                "total_news": len(data.get('news', [])),
                "total_discussions": len(data.get('discussions', []))
            }
        }
        return json.dumps(output, indent=2, ensure_ascii=False)


class HTMLFormatter:
    """Generate interactive HTML dashboard."""
    
    def format(self, query: str, data: Dict[str, List[Dict[str, Any]]], analysis: Dict[str, Any]) -> str:
        """Generate HTML dashboard."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report: {query}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{ margin: 0; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .summary {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-card .number {{
            font-size: 48px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-card .label {{
            color: #666;
            margin-top: 10px;
        }}
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .item {{
            padding: 15px;
            border-left: 4px solid #667eea;
            margin: 15px 0;
            background: #f9f9f9;
        }}
        .item h3 {{
            margin: 0 0 10px 0;
            color: #333;
        }}
        .item a {{
            color: #667eea;
            text-decoration: none;
        }}
        .item a:hover {{
            text-decoration: underline;
        }}
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}
        .tag {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Research Report: {query}</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <p>{analysis.get('summary', 'No summary available.')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="number">{len(data.get('papers', []))}</div>
            <div class="label">Academic Papers</div>
        </div>
        <div class="stat-card">
            <div class="number">{len(data.get('repositories', []))}</div>
            <div class="label">GitHub Repos</div>
        </div>
        <div class="stat-card">
            <div class="number">{len(data.get('news', []))}</div>
            <div class="label">News Articles</div>
        </div>
        <div class="stat-card">
            <div class="number">{len(data.get('discussions', []))}</div>
            <div class="label">Discussions</div>
        </div>
    </div>
"""
        
        # Key Findings
        if analysis.get('key_findings'):
            html += '    <div class="section">\n'
            html += '        <h2>Key Findings</h2>\n'
            html += '        <ul>\n'
            for finding in analysis['key_findings']:
                html += f'            <li>{finding}</li>\n'
            html += '        </ul>\n'
            html += '    </div>\n'
        
        # Papers
        if data.get('papers'):
            html += '    <div class="section">\n'
            html += f'        <h2>Academic Papers ({len(data["papers"])} found)</h2>\n'
            for paper in data['papers'][:10]:
                html += '        <div class="item">\n'
                html += f'            <h3><a href="{paper.get("link", "")}" target="_blank">{paper.get("title", "N/A")}</a></h3>\n'
                html += f'            <p><strong>Authors:</strong> {", ".join(paper.get("authors", [])[:5])}</p>\n'
                html += f'            <p>{paper.get("summary", "")[:300]}...</p>\n'
                html += '        </div>\n'
            html += '    </div>\n'
        
        # Repositories
        if data.get('repositories'):
            html += '    <div class="section">\n'
            html += f'        <h2>GitHub Repositories ({len(data["repositories"])} found)</h2>\n'
            for repo in data['repositories'][:10]:
                html += '        <div class="item">\n'
                html += f'            <h3><a href="{repo.get("url", "")}" target="_blank">{repo.get("title", "N/A")}</a></h3>\n'
                html += f'            <p>⭐ {repo.get("stars", 0)} stars | Language: {repo.get("language", "N/A")}</p>\n'
                html += f'            <p>{repo.get("description", "No description available.")}</p>\n'
                html += '        </div>\n'
            html += '    </div>\n'
        
        html += """
</body>
</html>
"""
        return html


class BibTeXFormatter:
    """Generate BibTeX citations."""
    
    def format(self, query: str, data: Dict[str, List[Dict[str, Any]]], analysis: Dict[str, Any]) -> str:
        """Generate BibTeX file."""
        import re
        entries = []
        
        for i, paper in enumerate(data.get('papers', []), 1):
            # Extract arXiv ID from link with validation
            link = paper.get('link', '')
            arxiv_id = f"unknown{i}"  # Default value
            if link:
                # Extract ID from various arXiv URL formats
                # http://arxiv.org/abs/1234.5678 or https://arxiv.org/abs/1234.5678v2
                match = re.search(r'arxiv.org/abs/(\d+\.\d+)', link)
                if match:
                    arxiv_id = match.group(1)
            
            entry = f"""@article{{{arxiv_id},
    title = {{{paper.get('title', 'Unknown')}}},
    author = {{{' and '.join(paper.get('authors', ['Unknown']))}}},
    year = {{{paper.get('published', '')[:4] if paper.get('published') else 'Unknown'}}},
    journal = {{arXiv preprint arXiv:{arxiv_id}}},
    url = {{{paper.get('link', '')}}}
}}
"""
            entries.append(entry)
        
        return "\n".join(entries)


class CSVFormatter:
    """Generate CSV for data analysis."""
    
    def format(self, query: str, data: Dict[str, List[Dict[str, Any]]], analysis: Dict[str, Any]) -> str:
        """Generate CSV file."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write papers
        writer.writerow(['Type', 'Title', 'Authors/Description', 'URL', 'Date/Stars', 'Source'])
        
        for paper in data.get('papers', []):
            writer.writerow([
                'Paper',
                paper.get('title', ''),
                ', '.join(paper.get('authors', [])[:3]),
                paper.get('link', ''),
                paper.get('published', ''),
                paper.get('source', '')
            ])
        
        for repo in data.get('repositories', []):
            writer.writerow([
                'Repository',
                repo.get('title', ''),
                repo.get('description', ''),
                repo.get('url', ''),
                str(repo.get('stars', 0)),
                repo.get('source', '')
            ])
        
        for article in data.get('news', []):
            writer.writerow([
                'News',
                article.get('title', ''),
                '',
                article.get('url', ''),
                article.get('published', ''),
                article.get('source', '')
            ])
        
        return output.getvalue()


class MermaidFormatter:
    """Generate Mermaid knowledge graph."""
    
    def format(self, query: str, data: Dict[str, List[Dict[str, Any]]], analysis: Dict[str, Any]) -> str:
        """Generate Mermaid diagram."""
        mermaid = ["graph TD"]
        mermaid.append(f'    QUERY["{query}"]')
        
        # Add categories
        if data.get('papers'):
            mermaid.append(f'    PAPERS["Papers: {len(data["papers"])}"]')
            mermaid.append('    QUERY --> PAPERS')
        
        if data.get('repositories'):
            mermaid.append(f'    REPOS["Repositories: {len(data["repositories"])}"]')
            mermaid.append('    QUERY --> REPOS')
        
        if data.get('news'):
            mermaid.append(f'    NEWS["News: {len(data["news"])}"]')
            mermaid.append('    QUERY --> NEWS')
        
        if data.get('discussions'):
            mermaid.append(f'    DISC["Discussions: {len(data["discussions"])}"]')
            mermaid.append('    QUERY --> DISC')
        
        # Add top items
        for i, paper in enumerate(data.get('papers', [])[:3], 1):
            title = paper.get('title', '')[:30].replace('"', "'")
            mermaid.append(f'    P{i}["{title}..."]')
            mermaid.append(f'    PAPERS --> P{i}')
        
        for i, repo in enumerate(data.get('repositories', [])[:3], 1):
            title = repo.get('title', '')[:30].replace('"', "'")
            mermaid.append(f'    R{i}["{title}"]')
            mermaid.append(f'    REPOS --> R{i}')
        
        return "\n".join(mermaid)


class OutputFormatter:
    """Main formatter orchestrator."""
    
    def __init__(self):
        self.markdown = MarkdownFormatter()
        self.json = JSONFormatter()
        self.html = HTMLFormatter()
        self.bibtex = BibTeXFormatter()
        self.csv = CSVFormatter()
        self.mermaid = MermaidFormatter()
    
    def generate_all(self, query: str, data: Dict[str, List[Dict[str, Any]]], analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate all output formats."""
        logger.info("Generating all output formats")
        
        return {
            'markdown': self.markdown.format(query, data, analysis),
            'json': self.json.format(query, data, analysis),
            'html': self.html.format(query, data, analysis),
            'bibtex': self.bibtex.format(query, data, analysis),
            'csv': self.csv.format(query, data, analysis),
            'mermaid': self.mermaid.format(query, data, analysis)
        }
