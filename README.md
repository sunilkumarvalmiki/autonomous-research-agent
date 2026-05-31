# Autonomous Research Agent

A Python research-agent project that combines local/open-source language models, retrieval-augmented
generation, multi-step reasoning, and evaluation scripts.

## Overview

Implemented Python project with demos, Docker support, tests, documentation, deployment notes, and
verification scripts.

## What This Repository Contains

- Agent source code under `src/`.
- Demo scripts and output examples at the repository root.
- Tests, pytest configuration, and coverage artifacts.
- Docker, docker-compose, setup, deployment, and running guides.

## Who This Is For

- Python AI developers
- RAG experimenters
- Researchers testing local LLM agents
- Maintainers building agent evaluation flows

## Repository Structure

| Path | Purpose |
|------|---------|
| `src/` | Research-agent implementation. |
| `tests/` | Automated test coverage. |
| `examples/` | Example usage material. |
| `docs/` | Supporting documentation. |
| `requirements.txt` | Python dependency list. |
| `Dockerfile` | Container build definition. |
| `docker-compose.yml` | Local multi-service orchestration. |

## Getting Started

- Create a Python virtual environment.
- Run `pip install -r requirements.txt`.
- Run `python demo_agent.py` for a simple demo path.
- Use `pytest` for the test suite when dependencies are installed.

## Common Workflows

- Use `RUNNING.md`, `GETTING_STARTED.md`, and `DEPLOYMENT.md` for operational details.
- Use Docker or docker-compose when you need an isolated runtime.

## Quality, Security, And Maintenance Notes

- Document which model backend is being used before comparing outputs.
- Keep model credentials, API keys, and private research corpora out of the repository.

## Current Documentation State

This README was rewritten to make the repository purpose, structure, setup path, and safety
expectations clear to a new reader. If implementation details change, update this file in the same
change so the GitHub landing page stays accurate.

Last documentation refresh: 2026-05-31.
