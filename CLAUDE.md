# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Setup: `pip install -e .` or `poetry install`
- Lint: `ruff check .`
- Format: `ruff format .`
- Type check: `mypy .`
- Test all: `pytest`
- Test single: `pytest tests/path/to/test_file.py::TestClass::test_method -v`
- Run API: `python -m src.api.main`

## Code Style Guidelines
- **Imports**: Group stdlib, third-party, then local imports with blank line between groups
- **Types**: Use type hints for all function parameters and return values
- **Naming**: 
  - snake_case for variables, functions, modules
  - PascalCase for classes and type vars
  - Interfaces/ABCs suffixed with Repository/Service
- **Architecture**: Follow Clean Architecture structure with core → application → infrastructure → api layers
- **Error handling**: Use specific exceptions from custom hierarchy, handle at boundaries
- **Repositories**: Implement core.repositories interfaces with concrete persistence logic
- **Testing**: Test business logic in isolation with mocked dependencies