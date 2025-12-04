# GitHub Lifecycle Management

Complete automation of GitHub repository lifecycle operations for production-grade DevOps.

## Overview

The GitHub Lifecycle Manager provides comprehensive automation for:

- **Pull Request Management** - Auto-merge, cleanup, status tracking
- **Issue Management** - Auto-labeling, assignment, closure
- **Branch Operations** - Creation, protection enforcement, synchronization
- **Release Management** - Semantic versioning, changelog generation
- **Workflow Orchestration** - Cross-workflow triggers, status monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│          GitHub Lifecycle Manager                        │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ PR Manager   │  │ Issue Mgr    │  │ Branch Mgr   │ │
│  │              │  │              │  │              │ │
│  │ • Auto-merge │  │ • Auto-label │  │ • Create     │ │
│  │ • Cleanup    │  │ • Assign     │  │ • Protect    │ │
│  │ • Status     │  │ • Close      │  │ • Sync       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────┐  ┌──────────────────────────────────┐ │
│  │ Release Mgr  │  │ Workflow Orchestrator            │ │
│  │              │  │                                  │ │
│  │ • Semantic   │  │ • Trigger workflows              │ │
│  │   versioning │  │ • Monitor status                 │ │
│  │ • Changelog  │  │ • Wait for completion            │ │
│  └──────────────┘  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Features

### 1. Pull Request Automation

**Auto-Merge Ready PRs**
- Checks if PR is mergeable
- Validates all status checks passed
- Merges with configurable method (squash/merge/rebase)
- Logs all operations

**Branch Cleanup**
- Automatically deletes branches after PR merge
- Prevents repository clutter
- Maintains clean branch history

**Example:**
```python
from src.github_lifecycle import get_lifecycle_manager

manager = get_lifecycle_manager()

# Auto-merge ready PRs
prs = manager.list_pull_requests()
for pr in prs:
    if manager.auto_merge_if_ready(pr['number']):
        print(f"Merged PR #{pr['number']}")

# Cleanup merged branches
deleted = manager.cleanup_merged_branches()
print(f"Deleted {len(deleted)} branches")
```

### 2. Issue Management

**Auto-Labeling**
- Detects research topics → `research` label
- Identifies priority → `priority:high/medium/low`
- Categorizes type → `type:bug/enhancement/documentation`

**Issue Lifecycle**
- Auto-assign based on expertise
- Close with summary comment
- Create follow-up issues

**Example:**
```python
# Auto-label an issue
labels = manager.auto_label_issue(issue_number=42)
print(f"Applied labels: {labels}")

# Close issue with comment
manager.close_issue(
    issue_number=42,
    comment="✅ Research completed. Results available in artifacts."
)
```

### 3. Branch Management

**Branch Creation**
```python
# Create feature branch from main
manager.create_branch('feature/new-capability', from_branch='main')
```

**Protection Enforcement**
```python
# Enforce branch protection rules
results = manager.enforce_branch_protections()
# Protects: main (strict), test (moderate), dev (minimal)
```

**Protection Levels:**

| Branch | Approvals | Status Checks | Admin Enforcement |
|--------|-----------|---------------|-------------------|
| main   | 2         | all-tests-passed, security-scan | Yes |
| test   | 1         | dev-ci | No |
| dev    | 0         | - | No |

### 4. Release Management

**Semantic Versioning**
- Automatic version bumping (major/minor/patch)
- Follows semver specification
- Tags and creates GitHub releases

**Changelog Generation**
- Groups PRs by type (features, bugfixes, docs)
- Includes PR numbers and links
- Markdown formatted

**Example:**
```python
# Create patch release (e.g., v1.2.3 → v1.2.4)
release = manager.create_semantic_release(version_bump='patch')

# Manual release with custom changelog
changelog = manager.generate_changelog(since_tag='v1.0.0')
manager.create_release(
    tag_name='v1.3.0',
    name='Release v1.3.0 - Production Improvements',
    body=changelog
)
```

**Changelog Format:**
```markdown
# Changelog

*Generated on 2025-12-04*

## ✨ Features

- Add production-grade observability (#15)
- Implement semantic memory with ChromaDB (#16)

## 🐛 Bug Fixes

- Fix UnboundLocalError in evaluation (#18)
- Improve arXiv ID extraction (#19)

## 📚 Documentation

- Add comprehensive testing guide (#20)
```

### 5. Workflow Orchestration

**Trigger Workflows**
```python
# Trigger research agent workflow
manager.trigger_workflow(
    workflow_id='research-agent.yml',
    ref='main',
    inputs={'topic': 'quantum computing', 'depth': 'deep'}
)
```

**Monitor Status**
```python
# Wait for checks to complete
success = manager.wait_for_checks(
    commit_sha='abc123',
    timeout_minutes=30
)

if success:
    print("All checks passed!")
```

## GitHub Actions Workflow

The lifecycle manager runs automatically via `.github/workflows/lifecycle-manager.yml`:

**Triggers:**
- **Schedule**: Daily at midnight UTC
- **Manual**: Workflow dispatch with operation selection
- **Pull Requests**: On opened/synchronized/reopened
- **Issues**: On opened/labeled

**Operations:**

| Operation | Description | Trigger |
|-----------|-------------|---------|
| `auto_merge_ready_prs` | Merge PRs with passing checks | Schedule, PR events |
| `cleanup_merged_branches` | Delete merged PR branches | Schedule |
| `auto_label_issues` | Apply smart labels | Issue events, schedule |
| `enforce_branch_protections` | Apply protection rules | Schedule |
| `create_release` | Generate semantic release | Manual only |
| `all` | Run all operations | Schedule, manual |

**Manual Trigger:**
```bash
# Via GitHub UI: Actions → GitHub Lifecycle Manager → Run workflow
# Select operation from dropdown

# Or via CLI:
gh workflow run lifecycle-manager.yml -f operation=auto_merge_ready_prs
```

## Configuration

### 1. GitHub PAT Setup

**Required Permissions:**
- `repo` (full control)
- `workflow` (trigger workflows)
- `admin:org` (manage protection rules, if org repo)

**Setup:**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with required permissions
3. Add to repository: Settings → Secrets and variables → Actions → New repository secret
4. Name: `GITHUB_PAT`
5. Value: Your PAT token

### 2. Environment Variables

The lifecycle manager uses these environment variables:

```bash
GITHUB_PAT        # Personal Access Token (preferred)
GITHUB_TOKEN      # Fallback to GitHub Actions token
GITHUB_REPOSITORY # Auto-set by GitHub Actions
```

### 3. Customization

**Custom Auto-Labeling Rules:**

Edit `src/github_lifecycle.py` → `auto_label_issue()` method:

```python
def auto_label_issue(self, issue_number: int) -> List[str]:
    issue = self.get_issue(issue_number)
    title = issue.get('title', '').lower()
    body = issue.get('body', '').lower()
    
    labels = []
    
    # Add your custom rules
    if 'ml' in title or 'machine learning' in body:
        labels.append('ai/ml')
    
    if 'devops' in title:
        labels.append('devops')
    
    # ... existing rules ...
    
    return labels
```

**Custom Branch Protection:**

Edit `src/github_lifecycle.py` → `enforce_branch_protections()` method to customize protection rules.

## Integration with Research Agent

The lifecycle manager integrates seamlessly with the autonomous research agent:

```python
# In src/main.py or research workflow

from src.github_lifecycle import get_lifecycle_manager

def run_research_with_lifecycle(issue_number: int, topic: str):
    manager = get_lifecycle_manager()
    
    # Auto-label the research issue
    manager.auto_label_issue(issue_number)
    
    # Run research
    results = run_research(topic)
    
    # Post results and close issue
    manager.create_issue_comment(issue_number, results['summary'])
    manager.close_issue(
        issue_number,
        comment="✅ Research complete. Check artifacts for full results."
    )
    
    # Trigger deployment if on main branch
    if results['quality_score'] > 0.8:
        manager.trigger_workflow('deploy.yml', ref='main')
```

## Best Practices

### 1. Security
- ✅ **Never** commit tokens to code
- ✅ Use repository secrets for PAT
- ✅ Limit PAT scope to minimum required permissions
- ✅ Rotate PATs regularly (every 90 days)
- ✅ Use fine-grained PATs when possible

### 2. Branch Strategy
- ✅ Enforce protections on `main`, `test` branches
- ✅ Require status checks before merge
- ✅ Use auto-merge only after validation
- ✅ Clean up branches regularly

### 3. Release Management
- ✅ Follow semantic versioning
- ✅ Generate comprehensive changelogs
- ✅ Tag releases consistently
- ✅ Create pre-releases for testing

### 4. Automation
- ✅ Start with manual triggers, then automate
- ✅ Monitor automation results
- ✅ Have fallback/rollback procedures
- ✅ Log all automated actions

## Monitoring

**Check Lifecycle Operations:**

```bash
# View workflow runs
gh run list --workflow=lifecycle-manager.yml

# View specific run details
gh run view <run-id>

# Check logs
gh run view <run-id> --log
```

**Metrics to Track:**
- PRs auto-merged per week
- Branches cleaned up
- Issues auto-labeled
- Average time to merge
- Release cadence

## Troubleshooting

### Issue: Auto-merge not working

**Solution:**
```python
# Check mergeable status
pr = manager.get_pull_request(pr_number)
print(f"Mergeable: {pr['mergeable']}")
print(f"Mergeable State: {pr['mergeable_state']}")

# Check status
status = manager._make_request('GET', f"/repos/{manager.repo}/commits/{pr['head']['sha']}/status")
print(f"Status: {status['state']}")
print(f"Checks: {status['statuses']}")
```

### Issue: Branch protection fails

**Solution:**
- Verify PAT has `admin:org` permission (for org repos)
- Check if branch exists: `gh api repos/{owner}/{repo}/branches`
- Ensure required checks exist in repository

### Issue: Workflow not triggering

**Solution:**
```bash
# Check workflow file syntax
gh workflow view lifecycle-manager.yml

# Manually trigger
gh workflow run lifecycle-manager.yml -f operation=all

# Check permissions
# Settings → Actions → General → Workflow permissions
```

## Examples

### Example 1: Complete PR Lifecycle

```python
from src.github_lifecycle import get_lifecycle_manager

manager = get_lifecycle_manager()

# Create feature branch
manager.create_branch('feature/new-datasource', from_branch='dev')

# ... development happens ...

# PR gets created (manually or via bot)
# PR number: 42

# Checks run automatically via CI/CD

# Auto-merge when ready
if manager.auto_merge_if_ready(42):
    print("PR merged!")
    
    # Cleanup branch
    manager.delete_branch('feature/new-datasource')
```

### Example 2: Issue-Driven Development

```python
# New issue created: #100
# Title: "Add support for PubMed API"

# Auto-label
labels = manager.auto_label_issue(100)
# Applied: ['research', 'type:enhancement', 'priority:medium']

# Create feature branch
manager.create_branch('feature/pubmed-api', from_branch='dev')

# ... development & testing ...

# Close issue when done
manager.close_issue(
    100,
    comment="✅ Implemented in #105. PubMed API now available!"
)
```

### Example 3: Release Workflow

```python
# All PRs merged to main
# Ready for release

# Generate changelog
changelog = manager.generate_changelog(since_tag='v2.0.0')

# Create release
release = manager.create_release(
    tag_name='v2.1.0',
    name='v2.1.0 - New Data Sources',
    body=changelog,
    prerelease=False
)

print(f"Release created: {release['html_url']}")

# Trigger deployment
manager.trigger_workflow('deploy-prod.yml', ref='main')
```

## Future Enhancements

Roadmap for additional lifecycle features:

- [ ] **Dependency Management** - Auto-update dependencies, create PRs
- [ ] **Security Scanning** - Auto-create issues for vulnerabilities
- [ ] **Stale Issue/PR Management** - Auto-close inactive items
- [ ] **Metrics Dashboard** - GitHub Pages dashboard with charts
- [ ] **Slack/Discord Integration** - Notifications for lifecycle events
- [ ] **Multi-Repo Coordination** - Sync across related repositories
- [ ] **A2A Integration** - Agent-to-agent communication protocols
- [ ] **Self-Healing** - Auto-fix common issues (merge conflicts, etc.)

## API Reference

See inline documentation in `src/github_lifecycle.py` for complete API reference.

**Key Classes:**
- `GitHubLifecycleManager` - Main lifecycle management class

**Key Methods:**
- `auto_merge_if_ready(pr_number)` - Auto-merge PR if checks pass
- `auto_label_issue(issue_number)` - Apply smart labels
- `create_semantic_release(version_bump)` - Create versioned release
- `enforce_branch_protections()` - Apply protection rules
- `trigger_workflow(workflow_id, ref, inputs)` - Trigger workflow dispatch

## Support

For issues or questions:
1. Check this documentation
2. Review `src/github_lifecycle.py` inline docs
3. Check GitHub Actions logs
4. Open an issue with label `lifecycle-manager`

---

**Status**: ✅ Production Ready

**Last Updated**: 2025-12-04

**Version**: 1.0.0
