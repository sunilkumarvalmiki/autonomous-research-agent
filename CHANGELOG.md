# Changelog

All notable changes to the autonomous-research-agent project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Production-grade CI/CD pipeline with comprehensive quality gates
- Automated branch cleanup workflow that deletes merged branches
- Automated branch promotion workflow (dev → test → main)
- Quality gates workflow with:
  - Code linting (Black, isort, Flake8, MyPy)
  - Security scanning (Bandit, Safety)
  - Multi-version testing (Python 3.10, 3.11, 3.12)
  - Build validation (package + Docker)
- Automated release workflow for main branch updates
- Pre-commit hooks configuration for local development
- Development dependencies (`requirements-dev.txt`)
- Unified tool configuration (`pyproject.toml`)
- This CHANGELOG.md to track changes

### Changed
- Updated `docs/BRANCHING_STRATEGY.md` with auto-cleanup and quality gates documentation

### Security
- Added Bandit security scanning to CI pipeline
- Added Safety dependency vulnerability scanning
- Security checks run on all PRs and branch pushes

## [0.1.0] - Initial Release

### Added
- Core autonomous research agent functionality
- LLM integration with open-source models
- Vector database integration (ChromaDB, FAISS)
- Self-improvement capabilities
- Basic CI/CD workflows
- Documentation and guides
- Docker support
- Example configurations

[Unreleased]: https://github.com/sunilkumarvalmiki/autonomous-research-agent/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sunilkumarvalmiki/autonomous-research-agent/releases/tag/v0.1.0
