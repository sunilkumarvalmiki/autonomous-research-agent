# Contributing to Autonomous Research Agent

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Pull Request Process](#pull-request-process)
7. [Coding Standards](#coding-standards)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

## Getting Started

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub
   git clone https://github.com/YOUR_USERNAME/autonomous-research-agent.git
   cd autonomous-research-agent
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

## Development Setup

1. **Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

2. **Install Ollama (optional)**
   ```bash
   # For testing with local models
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull llama3.1:8b
   ```

## Making Changes

### Types of Contributions

- **Bug Fixes**: Fix existing bugs
- **Features**: Add new functionality
- **Documentation**: Improve docs
- **Tests**: Add or improve tests
- **Performance**: Optimize existing code

### Before You Start

1. Check existing issues and PRs
2. Open an issue to discuss major changes
3. Ensure your change aligns with project goals

### Development Workflow

1. **Write Code**
   - Follow existing code structure
   - Add docstrings to functions/classes
   - Keep changes focused and minimal

2. **Add Tests**
   ```bash
   # Add tests in tests/ directory
   # Run tests
   python tests/run_tests.py
   ```

3. **Update Documentation**
   - Update README.md if needed
   - Add docstrings
   - Update GETTING_STARTED.md for user-facing changes

## Testing

### Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Run specific test file
python -m unittest tests/test_config.py

# Run specific test
python -m unittest tests.test_config.TestConfig.test_model_config_creation
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names
- Test edge cases
- Mock external dependencies

Example:
```python
import unittest

class TestMyFeature(unittest.TestCase):
    def test_basic_functionality(self):
        """Test basic feature works as expected."""
        result = my_function("input")
        self.assertEqual(result, "expected_output")
```

### Test Coverage

Aim for high test coverage:
```bash
# Install coverage
pip install coverage

# Run with coverage
coverage run -m unittest discover tests/
coverage report
coverage html  # Generate HTML report
```

## Pull Request Process

1. **Update your branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: Add new feature X"
   # Use conventional commits format
   ```

3. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**
   - Go to GitHub and create PR
   - Fill out the PR template
   - Link related issues
   - Request review

5. **Address Feedback**
   - Make requested changes
   - Push updates to same branch
   - Respond to comments

### PR Guidelines

- **Title**: Clear and descriptive
- **Description**: Explain what and why
- **Tests**: Include tests for new code
- **Documentation**: Update as needed
- **Small PRs**: Keep changes focused

### Commit Message Format

Use conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance

Examples:
```
feat(rag): Add support for FAISS vector database

Implements FAISS as an alternative to ChromaDB for better
performance with large datasets.

Closes #123
```

## Coding Standards

### Python Style

Follow PEP 8:
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable names
- Add type hints where appropriate

```python
def process_query(query: str, max_length: int = 100) -> str:
    """
    Process a query string.
    
    Args:
        query: The input query
        max_length: Maximum length of output
    
    Returns:
        Processed query string
    """
    return query[:max_length]
```

### Documentation

- Add docstrings to all public functions/classes
- Use Google-style docstrings
- Include examples in docstrings when helpful
- Keep README and docs up to date

### Code Organization

```
src/autonomous_agent/
├── __init__.py          # Package initialization
├── config.py            # Configuration management
├── models/              # Model implementations
├── agents/              # Agent implementations
├── rag/                 # RAG components
├── utils/               # Utility functions
└── evaluation/          # Evaluation metrics
```

### Error Handling

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
finally:
    cleanup()
```

## Areas for Contribution

### High Priority

1. **Model Integrations**
   - Add support for more open-source models
   - Implement model comparison tools
   - Add fine-tuning examples

2. **RAG Improvements**
   - Advanced retrieval strategies
   - Hybrid search implementation
   - Re-ranking mechanisms

3. **Self-Improvement**
   - Automated fine-tuning pipeline
   - Better feedback analysis
   - Performance tracking

### Medium Priority

1. **Documentation**
   - More examples
   - Video tutorials
   - Architecture deep-dives

2. **Testing**
   - Integration tests
   - Performance benchmarks
   - Model comparison tests

3. **Tools**
   - Web UI
   - Monitoring dashboard
   - Model benchmarking tool

### Good First Issues

Look for issues labeled `good-first-issue`:
- Documentation improvements
- Adding examples
- Writing tests
- Fixing typos

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create an issue with reproduction steps
- **Features**: Discuss in issues before implementing

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

Thank you for contributing! 🎉
