# 🔬 Autonomous Research Agent

A fully autonomous research agent that runs entirely on GitHub Actions. Just create an issue, and get comprehensive research reports automatically!

## ✨ Features

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

**Note**: You only need ONE of these API keys for the agent to work. Groq is recommended for best results.

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
│   └── workflows/
│       └── research-agent.yml    # GitHub Actions workflow
├── src/
│   ├── main.py                   # Orchestrator
│   ├── scraper.py                # Data collection
│   ├── analyzer.py               # LLM integration
│   ├── formatter.py              # Output generation
│   └── github_api.py             # GitHub API client
├── docs/
│   └── index.html                # GitHub Pages template
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🔧 Local Development

If you want to test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your-key-here"
export GITHUB_TOKEN="your-token-here"

# Run the agent
python src/main.py \
  --query "Machine Learning" \
  --output-dir ./outputs
```

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