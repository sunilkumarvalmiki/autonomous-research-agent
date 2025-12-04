"""
GitHub Lifecycle Management Module

Provides comprehensive GitHub automation for production-grade operations:
- Pull Request management (auto-merge, cleanup)
- Issue management (labeling, assignment, closure)
- Branch operations (creation, protection, sync)
- Release management (versioning, changelogs)
- Workflow orchestration
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubLifecycleManager:
    """Manages complete GitHub repository lifecycle operations."""
    
    def __init__(self, token: Optional[str] = None, repo: Optional[str] = None):
        """
        Initialize GitHub Lifecycle Manager.
        
        Args:
            token: GitHub PAT (falls back to GITHUB_PAT or GITHUB_TOKEN env var)
            repo: Repository in format "owner/repo" (falls back to GITHUB_REPOSITORY)
        """
        self.token = token or os.getenv('GITHUB_PAT') or os.getenv('GITHUB_TOKEN')
        self.repo = repo or os.getenv('GITHUB_REPOSITORY')
        
        if not self.token:
            raise ValueError("GitHub token not provided")
        if not self.repo:
            raise ValueError("Repository not specified")
            
        self.api_base = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Make GitHub API request with error handling."""
        url = f"{self.api_base}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response.raise_for_status()
            return response.json() if response.content else None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            raise
    
    # ============================================================================
    # PULL REQUEST MANAGEMENT
    # ============================================================================
    
    def list_pull_requests(self, state: str = 'open') -> List[Dict]:
        """List pull requests."""
        endpoint = f"/repos/{self.repo}/pulls?state={state}"
        return self._make_request('GET', endpoint)
    
    def get_pull_request(self, pr_number: int) -> Dict:
        """Get pull request details."""
        endpoint = f"/repos/{self.repo}/pulls/{pr_number}"
        return self._make_request('GET', endpoint)
    
    def merge_pull_request(self, pr_number: int, merge_method: str = 'squash') -> Dict:
        """
        Merge pull request.
        
        Args:
            pr_number: Pull request number
            merge_method: 'merge', 'squash', or 'rebase'
        """
        endpoint = f"/repos/{self.repo}/pulls/{pr_number}/merge"
        data = {'merge_method': merge_method}
        logger.info(f"Merging PR #{pr_number} with method '{merge_method}'")
        return self._make_request('PUT', endpoint, data)
    
    def auto_merge_if_ready(self, pr_number: int) -> bool:
        """
        Auto-merge PR if all checks pass.
        
        Returns:
            True if merged, False if not ready
        """
        pr = self.get_pull_request(pr_number)
        
        # Check if mergeable
        if not pr.get('mergeable'):
            logger.info(f"PR #{pr_number} is not mergeable")
            return False
        
        # Check status checks
        endpoint = f"/repos/{self.repo}/commits/{pr['head']['sha']}/status"
        status = self._make_request('GET', endpoint)
        
        if status.get('state') != 'success':
            logger.info(f"PR #{pr_number} status checks not passed: {status.get('state')}")
            return False
        
        # All checks passed, merge
        self.merge_pull_request(pr_number)
        logger.info(f"PR #{pr_number} auto-merged successfully")
        return True
    
    def delete_branch(self, branch: str) -> None:
        """Delete a branch."""
        endpoint = f"/repos/{self.repo}/git/refs/heads/{branch}"
        self._make_request('DELETE', endpoint)
        logger.info(f"Deleted branch: {branch}")
    
    def cleanup_merged_branches(self) -> List[str]:
        """Delete branches for merged PRs."""
        deleted = []
        prs = self.list_pull_requests(state='closed')
        
        for pr in prs:
            if pr.get('merged_at'):
                branch = pr['head']['ref']
                try:
                    self.delete_branch(branch)
                    deleted.append(branch)
                except Exception as e:
                    logger.warning(f"Could not delete branch {branch}: {e}")
        
        return deleted
    
    # ============================================================================
    # ISSUE MANAGEMENT
    # ============================================================================
    
    def list_issues(self, state: str = 'open', labels: Optional[List[str]] = None) -> List[Dict]:
        """List issues with optional label filter."""
        endpoint = f"/repos/{self.repo}/issues?state={state}"
        if labels:
            endpoint += f"&labels={','.join(labels)}"
        return self._make_request('GET', endpoint)
    
    def get_issue(self, issue_number: int) -> Dict:
        """Get issue details."""
        endpoint = f"/repos/{self.repo}/issues/{issue_number}"
        return self._make_request('GET', endpoint)
    
    def update_issue(self, issue_number: int, **kwargs) -> Dict:
        """
        Update issue (title, body, state, labels, assignees, etc.).
        
        Args:
            issue_number: Issue number
            **kwargs: Any of: title, body, state, labels, assignees, milestone
        """
        endpoint = f"/repos/{self.repo}/issues/{issue_number}"
        return self._make_request('PATCH', endpoint, kwargs)
    
    def close_issue(self, issue_number: int, comment: Optional[str] = None) -> Dict:
        """Close an issue with optional comment."""
        if comment:
            self.create_issue_comment(issue_number, comment)
        return self.update_issue(issue_number, state='closed')
    
    def create_issue_comment(self, issue_number: int, body: str) -> Dict:
        """Create comment on issue."""
        endpoint = f"/repos/{self.repo}/issues/{issue_number}/comments"
        return self._make_request('POST', endpoint, {'body': body})
    
    def auto_label_issue(self, issue_number: int) -> List[str]:
        """
        Automatically label issue based on content.
        
        Returns:
            List of applied labels
        """
        issue = self.get_issue(issue_number)
        title = issue.get('title', '').lower()
        body = issue.get('body', '').lower()
        
        labels = []
        
        # Research topic detection
        if 'research:' in title or 'research' in body:
            labels.append('research')
        
        # Priority detection
        if any(word in title or word in body for word in ['urgent', 'critical', 'asap']):
            labels.append('priority:high')
        elif any(word in title or word in body for word in ['low priority', 'minor']):
            labels.append('priority:low')
        else:
            labels.append('priority:medium')
        
        # Type detection
        if any(word in title for word in ['bug', 'error', 'issue', 'problem']):
            labels.append('type:bug')
        elif any(word in title for word in ['feature', 'enhancement', 'add']):
            labels.append('type:enhancement')
        elif any(word in title for word in ['doc', 'documentation']):
            labels.append('type:documentation')
        
        if labels:
            self.update_issue(issue_number, labels=labels)
            logger.info(f"Auto-labeled issue #{issue_number} with: {labels}")
        
        return labels
    
    # ============================================================================
    # BRANCH MANAGEMENT
    # ============================================================================
    
    def create_branch(self, branch_name: str, from_branch: str = 'main') -> Dict:
        """Create a new branch."""
        # Get the SHA of the source branch
        endpoint = f"/repos/{self.repo}/git/ref/heads/{from_branch}"
        ref = self._make_request('GET', endpoint)
        sha = ref['object']['sha']
        
        # Create new branch
        endpoint = f"/repos/{self.repo}/git/refs"
        data = {
            'ref': f'refs/heads/{branch_name}',
            'sha': sha
        }
        logger.info(f"Creating branch '{branch_name}' from '{from_branch}'")
        return self._make_request('POST', endpoint, data)
    
    def update_branch_protection(self, branch: str, protection_rules: Dict) -> Dict:
        """
        Update branch protection rules.
        
        Args:
            branch: Branch name
            protection_rules: Protection configuration dict
        """
        endpoint = f"/repos/{self.repo}/branches/{branch}/protection"
        return self._make_request('PUT', endpoint, protection_rules)
    
    def enforce_branch_protections(self) -> Dict[str, bool]:
        """Enforce branch protection rules for main, test, dev branches."""
        results = {}
        
        # Main branch - strictest protection
        main_protection = {
            'required_status_checks': {
                'strict': True,
                'contexts': ['all-tests-passed', 'security-scan']
            },
            'enforce_admins': True,
            'required_pull_request_reviews': {
                'required_approving_review_count': 2,
                'dismiss_stale_reviews': True
            },
            'restrictions': None,
            'required_linear_history': True,
            'allow_force_pushes': False,
            'allow_deletions': False
        }
        
        # Test branch - moderate protection
        test_protection = {
            'required_status_checks': {
                'strict': True,
                'contexts': ['dev-ci']
            },
            'enforce_admins': False,
            'required_pull_request_reviews': {
                'required_approving_review_count': 1
            },
            'restrictions': None,
            'allow_force_pushes': False
        }
        
        try:
            self.update_branch_protection('main', main_protection)
            results['main'] = True
            logger.info("Main branch protection enforced")
        except Exception as e:
            logger.error(f"Failed to protect main: {e}")
            results['main'] = False
        
        try:
            self.update_branch_protection('test', test_protection)
            results['test'] = True
            logger.info("Test branch protection enforced")
        except Exception as e:
            logger.error(f"Failed to protect test: {e}")
            results['test'] = False
        
        return results
    
    # ============================================================================
    # RELEASE MANAGEMENT
    # ============================================================================
    
    def list_releases(self) -> List[Dict]:
        """List all releases."""
        endpoint = f"/repos/{self.repo}/releases"
        return self._make_request('GET', endpoint)
    
    def create_release(self, tag_name: str, name: str, body: str, 
                      draft: bool = False, prerelease: bool = False) -> Dict:
        """
        Create a new release.
        
        Args:
            tag_name: Git tag for release (e.g., 'v1.0.0')
            name: Release name
            body: Release notes/changelog
            draft: Create as draft
            prerelease: Mark as prerelease
        """
        endpoint = f"/repos/{self.repo}/releases"
        data = {
            'tag_name': tag_name,
            'name': name,
            'body': body,
            'draft': draft,
            'prerelease': prerelease
        }
        logger.info(f"Creating release {tag_name}")
        return self._make_request('POST', endpoint, data)
    
    def generate_changelog(self, since_tag: Optional[str] = None) -> str:
        """
        Generate changelog from merged PRs.
        
        Args:
            since_tag: Generate changelog since this tag
        
        Returns:
            Markdown formatted changelog
        """
        prs = self.list_pull_requests(state='closed')
        
        # Filter merged PRs
        merged_prs = [pr for pr in prs if pr.get('merged_at')]
        
        # If since_tag provided, filter by date
        if since_tag:
            try:
                endpoint = f"/repos/{self.repo}/git/refs/tags/{since_tag}"
                tag_ref = self._make_request('GET', endpoint)
                # Would need to get commit date and filter, simplified here
            except Exception:
                logger.warning(f"Could not find tag {since_tag}, including all merged PRs")
        
        # Group by labels
        features = []
        bugfixes = []
        docs = []
        other = []
        
        for pr in merged_prs[:50]:  # Limit to recent 50
            title = pr['title']
            number = pr['number']
            labels = [l['name'] for l in pr.get('labels', [])]
            
            entry = f"- {title} (#{number})"
            
            if any('enhancement' in l or 'feature' in l for l in labels):
                features.append(entry)
            elif any('bug' in l or 'fix' in l for l in labels):
                bugfixes.append(entry)
            elif any('doc' in l for l in labels):
                docs.append(entry)
            else:
                other.append(entry)
        
        # Build changelog
        changelog = f"# Changelog\n\n"
        changelog += f"*Generated on {datetime.now().strftime('%Y-%m-%d')}*\n\n"
        
        if features:
            changelog += "## ✨ Features\n\n" + "\n".join(features) + "\n\n"
        if bugfixes:
            changelog += "## 🐛 Bug Fixes\n\n" + "\n".join(bugfixes) + "\n\n"
        if docs:
            changelog += "## 📚 Documentation\n\n" + "\n".join(docs) + "\n\n"
        if other:
            changelog += "## 🔧 Other Changes\n\n" + "\n".join(other) + "\n\n"
        
        return changelog
    
    def create_semantic_release(self, version_bump: str = 'patch') -> Optional[Dict]:
        """
        Create a semantic versioned release.
        
        Args:
            version_bump: 'major', 'minor', or 'patch'
        
        Returns:
            Release dict or None if failed
        """
        # Get latest release
        releases = self.list_releases()
        
        if releases:
            latest_tag = releases[0]['tag_name']
            # Parse version (assuming vX.Y.Z format)
            version_str = latest_tag.lstrip('v')
            major, minor, patch = map(int, version_str.split('.'))
        else:
            major, minor, patch = 0, 1, 0
        
        # Bump version
        if version_bump == 'major':
            major += 1
            minor = 0
            patch = 0
        elif version_bump == 'minor':
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        
        new_version = f"v{major}.{minor}.{patch}"
        
        # Generate changelog
        changelog = self.generate_changelog(releases[0]['tag_name'] if releases else None)
        
        # Create release
        return self.create_release(
            tag_name=new_version,
            name=f"Release {new_version}",
            body=changelog
        )
    
    # ============================================================================
    # WORKFLOW ORCHESTRATION
    # ============================================================================
    
    def trigger_workflow(self, workflow_id: str, ref: str = 'main', inputs: Optional[Dict] = None) -> Dict:
        """
        Trigger a workflow dispatch event.
        
        Args:
            workflow_id: Workflow file name or ID
            ref: Git ref to run workflow on
            inputs: Workflow inputs
        """
        endpoint = f"/repos/{self.repo}/actions/workflows/{workflow_id}/dispatches"
        data = {
            'ref': ref,
            'inputs': inputs or {}
        }
        logger.info(f"Triggering workflow {workflow_id} on {ref}")
        return self._make_request('POST', endpoint, data)
    
    def get_workflow_runs(self, workflow_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        """
        Get workflow runs.
        
        Args:
            workflow_id: Filter by workflow
            status: Filter by status (queued, in_progress, completed)
        """
        endpoint = f"/repos/{self.repo}/actions/runs"
        params = []
        if workflow_id:
            params.append(f"workflow_id={workflow_id}")
        if status:
            params.append(f"status={status}")
        if params:
            endpoint += "?" + "&".join(params)
        
        return self._make_request('GET', endpoint).get('workflow_runs', [])
    
    def wait_for_checks(self, commit_sha: str, timeout_minutes: int = 30) -> bool:
        """
        Wait for status checks to complete on a commit.
        
        Returns:
            True if all checks passed, False otherwise
        """
        import time
        timeout = datetime.now() + timedelta(minutes=timeout_minutes)
        
        while datetime.now() < timeout:
            endpoint = f"/repos/{self.repo}/commits/{commit_sha}/status"
            status = self._make_request('GET', endpoint)
            
            state = status.get('state')
            if state == 'success':
                logger.info(f"All checks passed for {commit_sha[:7]}")
                return True
            elif state == 'failure' or state == 'error':
                logger.error(f"Checks failed for {commit_sha[:7]}: {state}")
                return False
            
            # Still pending, wait
            logger.info(f"Waiting for checks on {commit_sha[:7]}... ({state})")
            time.sleep(30)
        
        logger.warning(f"Timeout waiting for checks on {commit_sha[:7]}")
        return False


# Convenience function
def get_lifecycle_manager() -> GitHubLifecycleManager:
    """Get initialized GitHub Lifecycle Manager."""
    return GitHubLifecycleManager()
