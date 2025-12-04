# Architecture Documentation

## System Overview

The Autonomous Research Agent is a production-grade, self-improving system designed to run on GitHub Actions with zero local installation required.

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                       GitHub Actions                            │
│                    (Execution Environment)                      │
└─────────────┬──────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Autonomous Research Agent                      │
│                    (Main Orchestrator)                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          Observability & Monitoring Layer                 │  │
│  │  • Performance tracking  • Metrics collection            │  │
│  │  • Trace management     • Error logging                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────┬────────────┬────────────┬──────────────────┐  │
│  │  Scraper   │  Analyzer  │ Formatter  │  GitHub API      │  │
│  │  Module    │  Module    │  Module    │  Module          │  │
│  └────────────┴────────────┴────────────┴──────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Production-Grade Enhancement Layer                │  │
│  │  ┌─────────────┬──────────────┬────────────────────┐    │  │
│  │  │   Memory    │  Evaluation  │  Retry & Resilience│    │  │
│  │  │   System    │  Framework   │  Logic              │    │  │
│  │  └─────────────┴──────────────┴────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                        Output & Artifacts                         │
│  • Markdown reports  • JSON data  • HTML dashboards              │
│  • Metrics reports   • Evaluation reports  • Cached data         │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Core Modules

#### Scraper (`src/scraper.py`)
- **Purpose**: Multi-source data collection
- **Data Sources**:
  - ArxivScraper: Academic papers from arXiv
  - GitHubScraper: Repositories and trends
  - HackerNewsScraper: Tech discussions
  - RedditScraper: Community insights
  - DevToScraper: Developer articles
  - RSSFeedScraper: Tech blog aggregation
- **Features**: Time-range filtering, focus modes, depth configuration

#### Analyzer (`src/analyzer.py`)
- **Purpose**: LLM-based synthesis
- **LLM Providers**:
  - GroqAnalyzer: Llama 3.3 70B (primary)
  - GeminiAnalyzer: Google Gemini (backup)
  - HuggingFaceAnalyzer: Open models (fallback)
- **Shared Functions**: `prepare_context()`, `fallback_analysis()`
- **Features**: Automatic fallback, context preparation, structured output

#### Formatter (`src/formatter.py`)
- **Purpose**: Multi-format output generation
- **Formatters**:
  - MarkdownFormatter: Comprehensive reports
  - JSONFormatter: Structured data
  - HTMLFormatter: Interactive dashboards
  - BibTeXFormatter: Academic citations
  - CSVFormatter: Data analysis
  - MermaidFormatter: Knowledge graphs
- **Features**: Template-based generation, validation

#### GitHub API (`src/github_api.py`)
- **Purpose**: GitHub integration
- **Functions**:
  - Post comments to issues
  - Add labels
  - Create formatted summaries
- **Features**: Error handling, authentication

### 2. Production Enhancement Modules

#### Observability (`src/observability.py`)
**Classes:**
- `ObservabilityManager`: Central metrics and trace management
- `PerformanceMonitor`: Context manager for automatic tracing
- `MetricType`: Enum for metric categories
- `AgentMetric`: Metric data structure
- `AgentTrace`: Trace data structure

**Capabilities:**
- Start/end traces for operations
- Record metrics (latency, cost, quality, errors)
- Export metrics to JSON
- Generate performance summaries
- Calculate quality scores

**Usage Pattern:**
```python
obs = ObservabilityManager()
with PerformanceMonitor(obs, "operation_name"):
    # Your code here
    pass
```

#### Memory (`src/memory.py`)
**Classes:**
- `VectorMemory`: Semantic search with ChromaDB
- `CacheManager`: TTL-based caching
- `AgentMemory`: Combined memory system

**Capabilities:**
- Store research with vector embeddings
- Semantic search for similar past research
- Cache expensive operations
- Session history tracking
- Context enrichment from memory

**Data Flow:**
```
Query → Search Similar → Get Context → Enhance Research
  ↓                                           ↓
Store Result ← Complete Research ← Analyze ← Collect Data
```

#### Evaluation (`src/evaluation.py`)
**Classes:**
- `ResearchEvaluator`: Comprehensive quality assessment

**Evaluation Dimensions:**
1. **Comprehensiveness** (0-1)
   - Source coverage
   - Quantity of results
   - Data completeness

2. **Relevance** (0-1)
   - Query-result alignment
   - Term overlap
   - Category-specific scores

3. **Analysis Quality** (0-1)
   - Section completeness
   - Finding depth
   - Summary quality

4. **Output Quality** (0-1)
   - Format completeness
   - Format validity
   - Content quality

**Scoring:**
- Excellent: ≥ 0.8
- Good: ≥ 0.6
- Fair: ≥ 0.4
- Needs Improvement: < 0.4

### 3. Main Orchestrator (`src/main.py`)

**Workflow Steps:**
1. **Initialization**: Load config, initialize components
2. **Memory Check**: Search for similar past research
3. **Data Scraping**: Collect from all sources (with retry)
4. **Quality Check**: Calculate data quality score
5. **Analysis**: LLM synthesis
6. **Output Generation**: Generate all formats
7. **Evaluation**: Assess quality, generate recommendations
8. **Memory Storage**: Store for future learning
9. **Save Outputs**: Write to files
10. **GitHub Integration**: Post results

**Enhanced Features:**
- Observability throughout workflow
- Automatic retry with exponential backoff
- Quality evaluation and recommendations
- Performance summaries
- Error resilience

## Data Flow

```
GitHub Issue (with 'research' label)
         │
         ▼
GitHub Actions Trigger
         │
         ▼
Parse Configuration (YAML front matter)
         │
         ▼
Initialize Components + Observability
         │
         ▼
Check Memory (similar past research)
         │
         ▼
┌────────────────────────────────┐
│  Data Collection (with retry)  │
│  • arXiv    • GitHub          │
│  • HN       • Reddit          │
│  • Dev.to   • RSS             │
└────────────┬───────────────────┘
             │
             ▼
   Calculate Data Quality
             │
             ▼
   LLM Analysis (Groq/Gemini/HF)
             │
             ▼
   Generate All Output Formats
             │
             ▼
   Quality Evaluation
   (Comprehensive scoring)
             │
             ▼
   Store in Memory
   (For future learning)
             │
             ▼
   Save Outputs
   • research_report.{md,json,html,bib,csv,mmd}
   • evaluation_report.json
   • metrics.json
             │
             ▼
   Post to GitHub Issue
   • Summary
   • Quality metrics
   • Performance data
   • Recommendations
```

## Technology Stack

### Core Technologies
- **Python 3.11+**: Main programming language
- **GitHub Actions**: Execution environment
- **Free LLMs**: Groq, Gemini, HuggingFace

### Dependencies
**Data Collection:**
- requests, beautifulsoup4, feedparser
- PyGithub for GitHub API

**LLM Integration:**
- groq, google-generativeai, huggingface-hub

**Production Features:**
- chromadb: Vector database
- tenacity: Retry logic
- opentelemetry-api/sdk: Observability
- langgraph, langchain: Future workflow enhancement

**Data Processing:**
- pandas, numpy: Data manipulation
- python-dateutil, PyYAML: Parsing

## Configuration

### Issue Body YAML Front Matter
```yaml
---
depth: quick | standard | deep
focus: papers | tools | trends | all
time_range: week | month | year
---
```

### Environment Variables
- `GROQ_API_KEY`: Groq API access
- `GEMINI_API_KEY`: Google Gemini access (optional)
- `HUGGINGFACE_API_KEY`: HuggingFace access (optional)
- `GITHUB_TOKEN`: GitHub API access (auto-provided)

### Command Line Arguments
```bash
--query              # Research topic (required)
--issue-body        # Issue body with config
--repo              # GitHub repo (owner/name)
--issue-number      # Issue number
--output-dir        # Output directory
--enable-memory     # Enable memory (default: true)
--enable-evaluation # Enable evaluation (default: true)
```

## Storage & Persistence

### Directories
- `./outputs/`: Research outputs
- `./agent_memory/`: Vector database
- `./cache/`: Cached API responses
- `./docs/`: GitHub Pages content

### Files Generated
**Per Research:**
- `research_report.md`: Markdown report
- `research_report.json`: JSON data
- `research_report.html`: HTML dashboard
- `research_report.bib`: BibTeX citations
- `research_report.csv`: CSV data
- `research_report.mmd`: Mermaid diagram
- `evaluation_report.json`: Quality assessment
- `metrics.json`: Performance metrics

## Security & Privacy

### API Keys
- Stored in GitHub Secrets
- Never logged or exposed
- Used only for authorized APIs

### Data Handling
- No sensitive data stored
- Public APIs only
- Results posted to requesting user's issue

### Rate Limiting
- Implements delays between requests
- Respects API rate limits
- Retry with exponential backoff

## Scalability Considerations

### Performance Optimizations
- Parallel data collection possible
- Caching reduces redundant requests
- Async support (aiohttp) for future enhancement

### Resource Management
- Configurable depth for different workloads
- Memory cleanup after completion
- Cache expiration (24h TTL)

### Monitoring
- Complete observability
- Performance tracking
- Error rate monitoring
- Quality metrics

## Future Architecture Enhancements

### Planned Improvements
1. **LangGraph Integration**
   - State machine workflows
   - Complex multi-step reasoning
   - Better error recovery

2. **Multi-Agent System**
   - Specialized agents (scraper, analyzer, evaluator)
   - Agent-to-agent communication (A2A protocol)
   - Coordinated workflows

3. **MCP Integration**
   - Model Context Protocol support
   - Tool/resource management
   - Better LLM integration

4. **Advanced RAG**
   - Knowledge base integration
   - Grounded generation
   - Reduced hallucinations

5. **Self-Improvement Loop**
   - Automatic optimization
   - Feedback incorporation
   - Continuous learning

## Design Patterns Used

### Patterns
- **Strategy Pattern**: Multiple LLM providers
- **Factory Pattern**: Scraper/formatter creation
- **Observer Pattern**: Observability tracking
- **Chain of Responsibility**: LLM fallback chain
- **Context Manager**: Performance monitoring
- **Retry Pattern**: Resilient data collection

### Principles
- **SOLID**: Clean, maintainable code
- **DRY**: Shared utilities (context preparation, fallback)
- **Separation of Concerns**: Modular architecture
- **Open/Closed**: Extensible for new sources/formats
- **Production-Ready**: Error handling, monitoring, quality

## Summary

This architecture provides:
✅ **Autonomous Operation**: Zero manual intervention
✅ **Production-Grade**: Monitoring, quality, resilience
✅ **Self-Improving**: Memory and learning
✅ **Scalable**: Modular, extensible design
✅ **Observable**: Complete visibility
✅ **Reliable**: Retry logic, error handling
✅ **High Quality**: Automated evaluation

The system is designed to operate reliably in production while continuously improving through learning and feedback.
