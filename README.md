# 🔬 Autonomous Research Agent

A **production-grade**, fully autonomous research agent that runs entirely on GitHub Actions. Features self-improvement, quality evaluation, and semantic memory for learning from past research!

## ✨ Core Features

- **Zero Installation**: Runs 100% on GitHub infrastructure
- **Issue-Triggered**: Create an issue with label "research" → Get results automatically
- **Multi-Source Data Collection**:
  - 📚 arXiv academic papers
  - 💻 GitHub trending repositories
  - 📰 HackerNews, Reddit, Dev.to
  - 🔖 RSS feeds from tech blogs
- **Free LLM Integration**:
  - Groq API (Llama 3.3 70B - generous free tier)
  - Google Gemini API (free tier)
  - HuggingFace Inference API
- **Rich Output Formats**:
  - 📄 Comprehensive Markdown reports
  - 📊 Structured JSON data
  - 🌐 Interactive HTML dashboards
  - 📚 BibTeX citations
  - 📈 CSV for data analysis
  - 🗺️ Knowledge graph visualizations (Mermaid)

## 🚀 Production-Grade Features

**NEW! The agent now includes enterprise-ready capabilities:**

### 🤖 GitHub Lifecycle Management (NEW!)
- **PR Automation**: Auto-merge ready PRs, branch cleanup
- **Issue Management**: Smart auto-labeling, auto-assignment, auto-closure
- **Branch Operations**: Auto-creation, protection enforcement
- **Release Management**: Semantic versioning, automated changelogs
- **Workflow Orchestration**: Cross-workflow triggers, status monitoring
- **Fully Autonomous**: Manages entire GitHub lifecycle 24/7

### 📊 Observability & Monitoring
- Complete performance tracking and metrics
- Trace every operation with start/end times
- Track latency, cost, accuracy, and error rates
- Export detailed metrics to JSON
- Performance summaries in GitHub comments

### 🧠 Memory & Learning
- **Semantic Memory**: Vector database for past research
- **Smart Caching**: 24-hour cache for expensive operations
- **Context Enrichment**: Recalls similar past research to enhance new queries
- Learns and improves over time

### ✅ Quality Evaluation
- Automated comprehensive quality assessment
- Evaluates: Comprehensiveness, Relevance, Analysis Quality, Output Quality
- Quality ratings: Excellent / Good / Fair / Needs Improvement
- Actionable recommendations for improvement

### 🔄 Resilience & Retry
- Automatic retry with exponential backoff
- Handles transient failures gracefully
- Production-grade error handling

### 📈 Enhanced Reporting
- Quality scores and ratings in every report
- Performance metrics included
- Detailed evaluation reports
- Self-improvement recommendations

**See [PRODUCTION_FEATURES.md](docs/PRODUCTION_FEATURES.md) for detailed documentation.**

## 🚀 Quick Start

### 1. Fork/Clone This Repository

```bash
git clone https://github.com/sunilkumarvalmiki/autonomous-research-agent.git
```

### 2. Add API Keys to GitHub Secrets

Go to your repository **Settings → Secrets and variables → Actions** and add:

| Secret Name | Description | Get It From |
|------------|-------------|-------------|
| `GROQ_API_KEY` | Groq API key (recommended) | [console.groq.com](https://console.groq.com) |
| `GEMINI_API_KEY` | Google Gemini API key | [makersuite.google.com](https://makersuite.google.com/app/apikey) |
| `HUGGINGFACE_API_KEY` | HuggingFace token (optional) | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `GITHUB_PAT` | Personal Access Token (for lifecycle management) | [GitHub Settings → Developer settings → PAT](https://github.com/settings/tokens) |

**Note**: 
- You only need ONE of the LLM API keys for research to work. Groq is recommended for best results.
- `GITHUB_PAT` is **optional** but enables advanced lifecycle management (auto-merge PRs, branch protection, releases, etc.). Requires `repo`, `workflow`, and `admin:org` (if applicable) scopes.

### 3. Enable GitHub Pages (Optional)

For interactive dashboards:
1. Go to **Settings → Pages**
2. Source: **GitHub Actions**
3. Save

### 4. Create a Research Issue

Create a new issue with:
- **Label**: `research` (required)
- **Title**: `Research: Your Topic Here`
- **Body**: Optional YAML configuration (see below)

Example:
```
Title: Research: Transformer Architecture in NLP

Body:
---
depth: deep
focus: papers
time_range: month
---
```

### 5. Watch the Magic! ✨

The agent will:
1. ✅ Automatically trigger on issue creation
2. 🔍 Scrape data from multiple sources
3. 🤖 Analyze with AI (Groq/Gemini/HuggingFace)
4. 📝 Generate comprehensive reports
5. 💬 Post summary to issue
6. 📦 Upload artifacts for download
7. 🌐 Deploy dashboard to GitHub Pages

## ⚙️ Configuration

Add YAML front matter to issue body for custom configuration:

```yaml
---
depth: quick | standard | deep
focus: papers | tools | trends | all
time_range: week | month | year
---
```

**Options:**

- `depth`:
  - `quick`: 20 papers, 15 repos, 10 news items
  - `standard` (default): 50 papers, 30 repos, 20 news items
  - `deep`: 100 papers, 50 repos, 40 news items

- `focus`:
  - `papers`: Academic papers only (arXiv)
  - `tools`: GitHub repositories only
  - `trends`: News, articles, discussions
  - `all` (default): Everything

- `time_range`:
  - `week`: Last 7 days
  - `month` (default): Last 30 days
  - `year`: Last 365 days

## 📦 Output Formats

All outputs are available as downloadable artifacts:

1. **research_report.md** - Comprehensive Markdown report
2. **research_report.json** - Structured JSON data
3. **research_report.html** - Interactive HTML dashboard
4. **research_report.bib** - BibTeX citations
5. **research_report.csv** - CSV for data analysis
6. **research_report.mmd** - Mermaid knowledge graph

## 🏗️ Project Structure

```
autonomous-research-agent/
├── .github/
│   ├── workflows/
│   │   ├── research-agent.yml      # Main research workflow
│   │   ├── lifecycle-manager.yml   # GitHub lifecycle automation
│   │   ├── dev-ci.yml              # Development CI
│   │   ├── test-ci.yml             # Comprehensive testing
│   │   └── prod-deploy.yml         # Production deployment
│   └── ISSUE_TEMPLATE/
│       └── research-request.md     # Issue template
├── src/
│   ├── main.py                     # Orchestrator
│   ├── scraper.py                  # Data collection
│   ├── analyzer.py                 # LLM integration
│   ├── formatter.py                # Output generation
│   ├── github_api.py               # GitHub API client
│   ├── github_lifecycle.py         # Lifecycle management (NEW!)
│   ├── observability.py            # Monitoring & metrics
│   ├── memory.py                   # Semantic memory
│   └── evaluation.py               # Quality evaluation
├── docs/
│   ├── index.html                  # GitHub Pages template
│   ├── PRODUCTION_FEATURES.md      # Production features guide
│   ├── ARCHITECTURE.md             # System architecture
│   ├── ROADMAP.md                  # Development roadmap
│   ├── BRANCHING_STRATEGY.md       # Branch strategy guide
│   ├── TESTING_GUIDE.md            # Testing documentation
│   └── GITHUB_LIFECYCLE.md         # Lifecycle management docs (NEW!)
├── tests/
│   ├── test_scraper.py             # Scraper tests
│   ├── test_observability.py       # Observability tests
│   └── test_evaluation.py          # Evaluation tests
├── scripts/
│   └── setup-branches.sh           # Branch setup script
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Pytest configuration
└── README.md                       # This file
```

## 🔧 Local Development

If you want to test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your-key-here"
export GITHUB_TOKEN="your-token-here"
export GITHUB_PAT="your-pat-here"  # Optional, for lifecycle management

# Run the agent
python src/main.py \
  --query "Machine Learning" \
  --output-dir ./outputs

# Test lifecycle management
python -c "
from src.github_lifecycle import get_lifecycle_manager
manager = get_lifecycle_manager()
print(manager.list_pull_requests())
"
```

## 📚 Documentation

- **[Production Features Guide](docs/PRODUCTION_FEATURES.md)** - Complete guide to observability, memory, and evaluation
- **[System Architecture](docs/ARCHITECTURE.md)** - Architecture overview and design patterns
- **[Development Roadmap](docs/ROADMAP.md)** - Future enhancements and phases
- **[Branching Strategy](docs/BRANCHING_STRATEGY.md)** - 3-branch strategy (dev→test→main)
- **[Testing Guide](docs/TESTING_GUIDE.md)** - 10 test types and how to run them
- **[GitHub Lifecycle Management](docs/GITHUB_LIFECYCLE.md)** - Complete lifecycle automation guide (NEW!)

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest new features
- 🔧 Submit pull requests
- 📚 Improve documentation

## 📄 License

MIT License - feel free to use this project however you like!

## 🙏 Acknowledgments

Built with:
- [Groq](https://groq.com) - Fast LLM inference
- [Google Gemini](https://deepmind.google/technologies/gemini/) - AI model
- [HuggingFace](https://huggingface.co) - ML platform
- [GitHub Actions](https://github.com/features/actions) - CI/CD automation
- [arXiv](https://arxiv.org) - Academic papers

## 📞 Support

- 📖 [Documentation](https://github.com/sunilkumarvalmiki/autonomous-research-agent)
- 🐛 [Issue Tracker](https://github.com/sunilkumarvalmiki/autonomous-research-agent/issues)
- 💬 [Discussions](https://github.com/sunilkumarvalmiki/autonomous-research-agent/discussions)

---

**Made with ❤️ by the open-source community**