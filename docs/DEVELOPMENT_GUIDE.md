# Development Guide

This guide describes how to develop and test features inside the monorepo structure.

## Setup Environment

Ensure Python 3.10+ is installed. Install all base dependencies:
```bash
pip install -r requirements.txt
```
For API development:
```bash
pip install -r quantum/requirements_api.txt
```

## Running Tests

Tests are localized under domains or the root `tests/` directory:
- Run all tests: `pytest`
- Run API tests: `pytest quantum/api/test_api.py`
- Run quantum tests: `pytest quantum/tests/`
- Run integration tests: `pytest tests/`

## Code Style & Formatting

Ruff is used for code linting and formatting. Ensure formatting rules are respected before pushing changes:
```bash
ruff check .
```
Ensure you do not commit raw data files, `.db` databases, or temporary logs to the root directory. Cleanliness is verified on CI.
