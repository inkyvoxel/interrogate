# Copilot Instructions for interrogate

## Project Overview
This is a Python package project for interrogating URLs, using modern tooling for dependency management and environment isolation. The package provides a CLI tool to validate and potentially extract information from URLs.

## Architecture
- **Package Structure**: Code organized under `src/interrogate/` as a proper Python package for distribution and reusability
- **Entry Points**: 
  - `main.py`: Development wrapper that imports from the package
  - `src/interrogate/__main__.py`: Main CLI logic with argument parsing
  - `pyproject.toml` defines `interrogate` console script pointing to `interrogate.__main__:main`
- **Core Components**: 
  - `validators.py`: URL validation utilities using `urllib.parse`
  - Simple validation flow: parse URL, check scheme and netloc, raise ValueError on invalid
- **Data Flow**: CLI argument `--url` → `validate_url()` → print success or error message
- **Why Package Structure**: Enables `pip install` for distribution, allows importing modules in tests and future extensions

## Development Environment
- Python version: >=3.14 (specified in `pyproject.toml`)
- Tool version management: `mise.toml` configures `uv` with automatic virtual environment creation
- Virtual environment: `.venv/` directory (auto-created by mise)

## Key Workflows
- **Run the CLI (dev)**: `uv run main.py --url https://example.com` or `uv run interrogate --url https://example.com`
- **Run the CLI (installed)**: After `pip install`, use `interrogate --url https://example.com`
- **Add dependencies**: Edit `pyproject.toml` dependencies array, then `uv sync`
- **Add dev dependencies**: `uv add --dev <package>` (e.g., `uv add --dev ruff`)
- **Run tests**: `uv run pytest` (configured in `pyproject.toml` with testpaths = ["tests"])
- **Lint code**: `uv run ruff check` (uses `ruff` from dev dependencies)
- **Format code**: `uv run ruff format`
- **Type check**: `uv run ty` (uses `ty` from dev dependencies)
- **Environment setup**: `mise install` to install tools and create venv, `uv sync` to install packages

## Conventions
- Use `uv` for all package operations (install, sync, etc.) and script execution (`uv run`) - do not use pip
- Use `ruff` for linting (`uv run ruff check`) and formatting (`uv run ruff format`)
- Use `ty` for type checking (`uv run ty`)
- Write typed Python code with type annotations for better type safety and IDE support
- Project configuration in `pyproject.toml` following PEP 621
- Version management via mise for reproducible environments
- Tests in `tests/` directory, mirroring source structure (e.g., `test_validators.py` for `validators.py`)
- URL validation raises `ValueError` with descriptive messages (e.g., "Invalid URL: Missing protocol")

## File Structure
- `main.py`: Development entry point importing from package
- `src/interrogate/__init__.py`: Package init with version
- `src/interrogate/__main__.py`: CLI argument parsing and main logic
- `src/interrogate/validators.py`: URL validation functions
- `tests/test_validators.py`: Unit tests for validators
- `pyproject.toml`: Project metadata, dependencies, scripts, and tool configs
- `mise.toml`: Tool configuration for uv
- `.python-version`: Python version pin (implied by mise)

## Integration Points
None currently - pure Python with standard library `urllib.parse`. Ready for extensions like HTTP requests or HTML parsing.