# Testing Guide

Comprehensive testing strategy for the autonomous research agent.

## Test Structure

```
tests/
├── __init__.py
├── test_scraper.py         # Unit tests for data collection
├── test_analyzer.py        # Unit tests for LLM analysis
├── test_formatter.py       # Unit tests for output generation
├── test_observability.py   # Unit tests for monitoring
├── test_memory.py          # Unit tests for memory system
├── test_evaluation.py      # Unit tests for quality assessment
├── integration/            # Integration tests
├── functional/             # Functional tests
└── performance/            # Performance tests
```

## Running Tests

### Quick Test (Dev Branch)

```bash
# Run all unit tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_scraper.py -v

# Run specific test
pytest tests/test_scraper.py::TestDataScraper::test_initialization -v
```

### Comprehensive Tests (Test Branch)

```bash
# Run all tests with full coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Run with performance profiling
pytest tests/ --durations=10

# Run with timeout protection
pytest tests/ --timeout=30
```

### Test by Category

```bash
# Unit tests only
pytest tests/ -m unit

# Integration tests
pytest tests/ -m integration

# Performance tests
pytest tests/ -m performance

# Smoke tests
pytest tests/ -m smoke
```

## Test Types

### 1. Unit Tests

**Purpose**: Test individual functions and classes in isolation

**Location**: `tests/test_*.py`

**Example**:
```python
def test_initialization():
    """Test component initializes correctly."""
    scraper = DataScraper()
    assert scraper is not None
```

**Run**:
```bash
pytest tests/test_scraper.py -v
```

### 2. Integration Tests

**Purpose**: Test interaction between components

**Example**:
```python
def test_component_integration():
    """Test multiple components working together."""
    scraper = DataScraper()
    analyzer = ResearchAnalyzer()
    formatter = OutputFormatter()
    
    data = scraper.scrape_all("test", "all", "month", "quick")
    analysis = analyzer.analyze(data, "test")
    outputs = formatter.generate_all("test", data, analysis)
    
    assert len(outputs) == 6
```

**Run**:
```bash
pytest tests/integration/ -v
```

### 3. Functional Tests

**Purpose**: Test complete features and workflows

**Example**:
```python
def test_config_parsing_workflow():
    """Test YAML configuration parsing."""
    config = parse_issue_config("---\ndepth: deep\n---")
    assert config['depth'] == 'deep'
```

**Run**:
```bash
pytest tests/functional/ -v
```

### 4. Performance Tests

**Purpose**: Measure speed and resource usage

**Example**:
```python
def test_observability_performance():
    """Test observability overhead is acceptable."""
    obs = ObservabilityManager()
    
    start = time.time()
    for i in range(1000):
        trace_id = obs.start_trace(f'op_{i}')
        obs.end_trace(trace_id, 'success')
    duration = time.time() - start
    
    assert duration < 5.0  # Should complete in < 5s
```

**Run**:
```bash
pytest tests/performance/ -v
```

### 5. Regression Tests

**Purpose**: Ensure bugs don't reappear and features don't break

**Example**:
```python
def test_backward_compatibility():
    """Test all legacy interfaces still work."""
    # Import using old interface
    from analyzer import prepare_context, fallback_analysis
    
    # Should not raise ImportError
    assert callable(prepare_context)
    assert callable(fallback_analysis)
```

### 6. Sanity Tests

**Purpose**: Quick validation that system is basically functional

**Example**:
```bash
python -c "from scraper import DataScraper; print('OK')"
python -c "from analyzer import ResearchAnalyzer; print('OK')"
```

### 7. Smoke Tests

**Purpose**: Verify critical functionality works

**Example**:
```python
def test_critical_path():
    """Test the most critical user path."""
    # Can we import?
    from main import parse_issue_config
    
    # Can we parse config?
    config = parse_issue_config("---\ndepth: quick\n---")
    
    # Did it work?
    assert config['depth'] == 'quick'
```

### 8. UAT (User Acceptance Tests)

**Purpose**: Simulate real user scenarios

**Example**:
```python
def test_user_creates_research_issue():
    """Simulate user creating research issue."""
    # User creates issue
    title = "Research: Machine Learning"
    body = "---\ndepth: standard\nfocus: papers\n---"
    
    # System processes
    query = extract_query_from_title(title)
    config = parse_issue_config(body)
    
    # Verify correct interpretation
    assert query == "Machine Learning"
    assert config['depth'] == 'standard'
    assert config['focus'] == 'papers'
```

### 9. Security Tests

**Purpose**: Find vulnerabilities and security issues

**Tools**:
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **CodeQL**: Static analysis
- **TruffleHog**: Secret scanning

**Run**:
```bash
# Bandit scan
bandit -r src/ -ll

# Dependency check
safety check

# Secret scanning (via GitHub Actions)
```

### 10. Load Tests

**Purpose**: Test system under heavy load

**Example**:
```python
def test_concurrent_operations():
    """Test handling multiple concurrent operations."""
    import concurrent.futures
    
    obs = ObservabilityManager()
    
    def operation(i):
        trace_id = obs.start_trace(f'op_{i}')
        time.sleep(0.01)
        obs.end_trace(trace_id, 'success')
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(operation, i) for i in range(100)]
        concurrent.futures.wait(futures)
    
    assert len(obs.traces) == 100
```

## Coverage Requirements

### Dev Branch
- **Minimum**: 60%
- **Target**: 70%

### Test Branch
- **Minimum**: 70%
- **Target**: 80%

### Main Branch
- **Minimum**: 80%
- **Target**: 90%

## Coverage Report

```bash
# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html

# Generate terminal report
pytest tests/ --cov=src --cov-report=term-missing
```

## Continuous Testing

### Pre-commit Checks

```bash
# Create .pre-commit-config.yaml
pre-commit install
pre-commit run --all-files
```

### Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw tests/ src/
```

## Test Data

### Mock Data

Use mocks for external dependencies:

```python
from unittest.mock import Mock, patch

@patch('requests.get')
def test_api_call(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': 'test'}
    mock_get.return_value = mock_response
    
    # Your test code
```

### Fixtures

Use pytest fixtures for reusable test data:

```python
@pytest.fixture
def sample_data():
    return {
        'papers': [{'title': 'Test', 'source': 'arXiv'}],
        'repositories': [],
        'news': [],
        'discussions': []
    }

def test_with_fixture(sample_data):
    assert len(sample_data['papers']) == 1
```

## CI/CD Integration

### GitHub Actions Workflows

#### Dev CI (`dev-ci.yml`)
- Runs on: push to dev, PR to dev
- Tests: lint, format, unit tests, smoke tests
- Duration: ~2-3 minutes

#### Test CI (`test-ci.yml`)
- Runs on: push to test, PR to test
- Tests: all comprehensive tests
- Duration: ~5-10 minutes

#### Prod Deploy (`prod-deploy.yml`)
- Runs on: push to main, PR to main
- Tests: final smoke tests, health checks
- Duration: ~2 minutes

## Debugging Failed Tests

### View Detailed Output

```bash
# Verbose mode
pytest tests/test_scraper.py -v

# Show print statements
pytest tests/test_scraper.py -s

# Stop at first failure
pytest tests/ -x

# Show locals in traceback
pytest tests/ -l
```

### Debug Mode

```python
def test_something():
    import pdb; pdb.set_trace()  # Breakpoint
    # Your test code
```

### Logging

```bash
# Show log output
pytest tests/ --log-cli-level=DEBUG
```

## Best Practices

### Writing Tests

✅ **Do**:
- Write descriptive test names
- Test one thing per test
- Use meaningful assertions
- Clean up resources
- Mock external dependencies
- Add docstrings to tests

❌ **Don't**:
- Test implementation details
- Write flaky tests
- Ignore test failures
- Skip writing tests
- Leave commented code
- Hard-code values

### Example Test

```python
def test_evaluate_comprehensiveness_with_complete_data():
    """
    Test comprehensiveness evaluation returns high score
    when data includes all source types.
    """
    # Arrange
    evaluator = ResearchEvaluator()
    complete_data = {
        'papers': [{'title': 'Paper', 'source': 'arXiv'}],
        'repositories': [{'title': 'Repo', 'source': 'GitHub'}],
        'news': [{'title': 'News', 'source': 'HN'}],
        'discussions': [{'title': 'Discussion', 'source': 'Reddit'}]
    }
    
    # Act
    score, details = evaluator.evaluate_comprehensiveness(complete_data)
    
    # Assert
    assert score > 0.7, f"Expected score > 0.7, got {score}"
    assert details['source_coverage']['present'] == 4
    assert details['source_coverage']['total'] == 4
```

## Test Metrics

### Track:
- **Test count**: Number of tests
- **Coverage**: Code coverage percentage
- **Duration**: Time to run tests
- **Flakiness**: Tests that fail intermittently
- **Failures**: Number of failing tests

### Goals:
- 📈 Increase test count over time
- 📊 Maintain >80% coverage
- ⚡ Keep test suite fast (<10 min)
- 🎯 Zero flaky tests
- ✅ Zero failures in main

## Troubleshooting

### Tests Won't Run

```bash
# Check pytest installation
pytest --version

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt
```

### Import Errors

```bash
# Verify src in path
export PYTHONPATH="${PYTHONPATH}:./src"

# Or use pytest with src in path
python -m pytest tests/
```

### Slow Tests

```bash
# Find slow tests
pytest tests/ --durations=10

# Run in parallel
pip install pytest-xdist
pytest tests/ -n auto
```

## Summary

This testing strategy ensures:
- 🧪 Comprehensive test coverage
- 🚀 Fast feedback loops
- 🛡️ High confidence in changes
- 📊 Measurable quality metrics
- 🔄 Continuous improvement

Follow the 3-branch strategy:
- **dev**: Quick validation
- **test**: Comprehensive testing
- **main**: Production quality
