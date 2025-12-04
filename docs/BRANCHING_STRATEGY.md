# Branch Protection Rules and Workflow Strategy

This document describes the 3-branch strategy for the autonomous research agent.

## Branch Strategy

### Branch Structure

```
main (production)
  ↑
  │ (PR after all tests pass)
  │
test (testing/staging)
  ↑
  │ (PR after development complete)
  │
dev (development)
```

### Branch Purposes

#### 1. `main` - Production Branch
- **Purpose**: Production-ready code only
- **Protection**: 
  - Require pull request reviews
  - Require status checks to pass
  - No direct pushes allowed
  - Require branches to be up to date
- **Deployment**: Automatically deploys to production
- **Access**: Only maintainers can merge

#### 2. `test` - Testing/Staging Branch
- **Purpose**: Integration testing and QA
- **Protection**:
  - Require pull request reviews
  - Require status checks to pass
  - No direct pushes allowed
- **Testing**: All comprehensive tests run here
- **Access**: Developers can create PRs, maintainers merge

#### 3. `dev` - Development Branch
- **Purpose**: Active development work
- **Protection**: 
  - Require pull request for merges (optional)
  - Basic CI checks
- **Testing**: Unit tests and basic validation
- **Access**: All developers can push (or via PR)

## Workflow

### Development Flow

```
1. Create feature branch from dev
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature

2. Develop and commit changes
   git add .
   git commit -m "feat: your feature"

3. Push and create PR to dev
   git push origin feature/your-feature
   # Create PR: feature/your-feature → dev

4. After dev PR approved and merged
   # Create PR: dev → test

5. After all tests pass in test
   # Create PR: test → main
```

## Testing Strategy

### Tests on `dev` Branch

**Quick Validation:**
- ✅ Syntax validation (pylint, flake8)
- ✅ Unit tests
- ✅ Basic smoke tests
- ✅ Code formatting (black, isort)

**Purpose**: Catch obvious errors early

### Tests on `test` Branch

**Comprehensive Testing:**

#### 1. Unit Tests
- All module tests
- Function-level tests
- Edge cases and error handling
- Code coverage > 80%

#### 2. Integration Tests
- Component interaction tests
- API integration tests
- Database/memory integration
- LLM provider integration

#### 3. Functional Tests
- End-to-end workflow tests
- Feature validation
- Output format validation
- Configuration parsing tests

#### 4. Performance Tests
- Latency measurements
- Memory usage profiling
- API call optimization
- Cache effectiveness

#### 5. Regression Tests
- Previous bug fixes validation
- Backward compatibility
- Feature parity checks

#### 6. Sanity Tests
- Basic functionality check
- Critical path validation
- Smoke test suite

#### 7. Smoke Tests
- Can the system start?
- Basic operations work?
- Critical features accessible?

#### 8. UAT (User Acceptance Testing)
- Real-world scenario tests
- Example research queries
- Output quality validation
- User workflow simulation

#### 9. Security Tests
- Dependency vulnerability scanning
- CodeQL security analysis
- API key handling validation
- Input sanitization tests

#### 10. Load Tests
- Concurrent request handling
- Rate limiting validation
- Resource cleanup

**Purpose**: Ensure production readiness

### Tests on `main` Branch

**Post-Deployment Validation:**
- ✅ Smoke tests
- ✅ Health checks
- ✅ Monitoring validation
- ✅ Rollback readiness

## CI/CD Pipeline

### GitHub Actions Workflows

#### 1. `dev-ci.yml` - Development CI
```yaml
triggers:
  - push to dev
  - PR to dev

jobs:
  - lint
  - format-check
  - unit-tests
  - smoke-tests
```

#### 2. `test-ci.yml` - Comprehensive Testing
```yaml
triggers:
  - push to test
  - PR to test

jobs:
  - all-unit-tests
  - integration-tests
  - functional-tests
  - performance-tests
  - regression-tests
  - security-scan
  - uat-tests
```

#### 3. `prod-deploy.yml` - Production Deployment
```yaml
triggers:
  - push to main
  - PR to main

jobs:
  - final-smoke-tests
  - deploy-production
  - health-check
  - monitor
```

## Branch Protection Configuration

### Protecting `main` Branch

```yaml
Branch protection rules for main:
  - Require pull request reviews before merging: ✓
  - Required number of approvals: 2
  - Dismiss stale pull request approvals: ✓
  - Require status checks to pass before merging: ✓
    Required checks:
      - all-tests-passed
      - security-scan-passed
      - performance-acceptable
  - Require branches to be up to date before merging: ✓
  - Require conversation resolution before merging: ✓
  - Include administrators: ✓
  - Restrict pushes: ✓
  - Allow force pushes: ✗
  - Allow deletions: ✗
```

### Protecting `test` Branch

```yaml
Branch protection rules for test:
  - Require pull request reviews before merging: ✓
  - Required number of approvals: 1
  - Require status checks to pass before merging: ✓
    Required checks:
      - dev-ci-passed
      - basic-tests-passed
  - Include administrators: ✓
  - Restrict pushes: ✓
  - Allow force pushes: ✗
```

### `dev` Branch Settings

```yaml
Branch settings for dev:
  - Optional: Require pull request for merges
  - Basic CI checks
  - Flexible for rapid development
```

## Manual Setup Instructions

### 1. Create Branches

```bash
# Ensure you're on main
git checkout main

# Create and push test branch
git checkout -b test
git push -u origin test

# Create and push dev branch
git checkout -b dev
git push -u origin dev
```

### 2. Configure Branch Protection

Go to GitHub → Repository → Settings → Branches

**For `main` branch:**
1. Click "Add rule"
2. Branch name pattern: `main`
3. Enable all protections listed above
4. Save

**For `test` branch:**
1. Click "Add rule"
2. Branch name pattern: `test`
3. Enable protections listed above
4. Save

### 3. Set Default Branch

- Go to Settings → General
- Set default branch to `dev`
- This ensures PRs default to dev

## Workflow Examples

### Example 1: New Feature

```bash
# 1. Start from dev
git checkout dev
git pull origin dev

# 2. Create feature branch
git checkout -b feature/add-langraph-integration

# 3. Develop
# ... make changes ...
git add .
git commit -m "feat: add LangGraph integration"

# 4. Push and PR to dev
git push origin feature/add-langraph-integration
# Create PR on GitHub: feature/add-langraph-integration → dev

# 5. After dev merge, PR to test
# Create PR on GitHub: dev → test

# 6. Wait for all tests to pass

# 7. After test success, PR to main
# Create PR on GitHub: test → main
```

### Example 2: Hotfix

```bash
# 1. Branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-fix

# 2. Fix
git add .
git commit -m "fix: critical bug in analyzer"

# 3. PR directly to main (emergency)
git push origin hotfix/critical-bug-fix
# Create PR: hotfix/critical-bug-fix → main

# 4. After merge, sync other branches
git checkout test
git merge main

git checkout dev
git merge test
```

## Testing Checklist

### Before PR to test:
- [ ] All unit tests pass locally
- [ ] Code is linted and formatted
- [ ] New features have tests
- [ ] Documentation updated
- [ ] No commented-out code
- [ ] No debug statements

### Before PR to main:
- [ ] All comprehensive tests pass
- [ ] Performance is acceptable
- [ ] Security scan clean
- [ ] UAT scenarios validated
- [ ] Rollback plan ready
- [ ] Monitoring configured

## Monitoring and Alerts

### Development (dev)
- Build failures → Slack/Email
- Test failures → Slack

### Testing (test)
- Any test failure → Block merge
- Performance regression → Alert
- Security issues → Block + Alert

### Production (main)
- Deployment failures → Page
- Health check failures → Alert
- Performance degradation → Monitor

## Best Practices

### Do:
- ✅ Always branch from dev for new features
- ✅ Keep PRs small and focused
- ✅ Write tests for new code
- ✅ Update documentation
- ✅ Review test results before merging
- ✅ Use meaningful commit messages

### Don't:
- ❌ Push directly to test or main
- ❌ Skip tests
- ❌ Merge failing PRs
- ❌ Deploy without testing
- ❌ Ignore security warnings
- ❌ Rush to production

## Rollback Strategy

### If Production Issue Detected:

```bash
# 1. Immediate rollback
git checkout main
git revert HEAD
git push origin main

# 2. Or revert to specific commit
git checkout main
git reset --hard <last-good-commit>
git push origin main --force-with-lease

# 3. Fix in dev and follow normal flow
git checkout dev
# ... fix issue ...
# Follow dev → test → main flow
```

## Summary

This 3-branch strategy ensures:
- 🛡️ Production stability
- 🧪 Comprehensive testing
- 🚀 Rapid development
- 🔒 Protected branches
- 📊 Quality gates
- 🔄 Smooth deployments

The flow dev → test → main ensures every change is thoroughly validated before reaching production.
