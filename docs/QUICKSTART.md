# Quick Start Guide

## 1. Setup (One-time)

### Add API Keys to Secrets

1. Go to your repository **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add at least ONE of these (Groq recommended):

| Secret Name | Where to Get It | Required? |
|------------|----------------|-----------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | Recommended ⭐ |
| `GEMINI_API_KEY` | [makersuite.google.com](https://makersuite.google.com/app/apikey) | Optional |
| `HUGGINGFACE_API_KEY` | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) | Optional |

### Enable GitHub Pages (Optional, for dashboards)

1. Go to **Settings → Pages**
2. Under **Source**, select **GitHub Actions**
3. Save

## 2. Create a Research Issue

### Option A: Use the Template

1. Click **Issues → New Issue**
2. Select **Research Request** template
3. Fill in your topic
4. Submit

### Option B: Manual

1. Create a new issue
2. Title: `Research: Your Topic Here`
3. Add label: `research`
4. Optionally add YAML configuration in the body:

```yaml
---
depth: deep
focus: papers
time_range: month
---
```

## 3. Wait for Results

The agent will automatically:
- ✅ Trigger within seconds
- 🔍 Scrape multiple data sources (takes 2-5 minutes)
- 🤖 Analyze with AI
- 📝 Generate reports
- 💬 Post summary to your issue
- 📦 Upload downloadable artifacts
- 🌐 Deploy dashboard to GitHub Pages (if enabled)

## 4. Access Your Results

### In the Issue
- Summary with key findings
- Knowledge graph visualization
- Links to artifacts

### Downloadable Artifacts
1. Go to **Actions** tab
2. Find your workflow run
3. Scroll to **Artifacts** section
4. Download `research-report-{issue_number}.zip`

Contains:
- 📄 `research_report.md` - Comprehensive Markdown report
- 📊 `research_report.json` - Structured JSON data
- 🌐 `research_report.html` - Interactive HTML dashboard
- 📚 `research_report.bib` - BibTeX citations
- 📈 `research_report.csv` - CSV for analysis
- 🗺️ `research_report.mmd` - Mermaid knowledge graph

### GitHub Pages Dashboard
If enabled, visit:
```
https://{your-username}.github.io/{repo-name}/research-{issue-number}/
```

## Configuration Options

### Depth
- `quick` - Fast scan (20 papers, 15 repos, 10 news)
- `standard` - Balanced (50 papers, 30 repos, 20 news) ⭐ Default
- `deep` - Comprehensive (100 papers, 50 repos, 40 news)

### Focus
- `papers` - Academic papers only (arXiv)
- `tools` - GitHub repositories only
- `trends` - News, articles, discussions
- `all` - Everything ⭐ Default

### Time Range
- `week` - Last 7 days
- `month` - Last 30 days ⭐ Default
- `year` - Last 365 days

## Examples

### Example 1: Quick Research on Trending Tools
```yaml
---
depth: quick
focus: tools
time_range: week
---
```

### Example 2: Deep Academic Research
```yaml
---
depth: deep
focus: papers
time_range: year
---
```

### Example 3: Comprehensive Overview
```yaml
---
depth: standard
focus: all
time_range: month
---
```

## Troubleshooting

### Workflow doesn't trigger
- ✓ Check if issue has `research` label
- ✓ Verify workflow file exists in `.github/workflows/`
- ✓ Check Actions tab for any errors

### No results posted
- ✓ Check workflow logs in Actions tab
- ✓ Verify at least one API key is added to secrets
- ✓ Check if query returned any results

### Poor quality analysis
- ✓ Add Groq API key for best results (free tier is generous)
- ✓ Use more specific search terms
- ✓ Adjust time_range if no recent results

## Advanced Usage

### Custom Subreddits
Edit `src/scraper.py` to search specific subreddits:
```python
results['discussions'] = self.reddit.search(query, subreddit='MachineLearning', max_results=limit['news'])
```

### Add More RSS Feeds
Edit `src/scraper.py` and add to `RSSFeedScraper.FEEDS`:
```python
FEEDS = [
    "https://your-blog.com/feed",
    # ... existing feeds
]
```

### Customize Output Formats
Edit `src/formatter.py` to modify report templates

## Need Help?

- 📖 [Full Documentation](../README.md)
- 🐛 [Report Issues](../../issues)
- 💬 [Discussions](../../discussions)
