# Contributing

Thank you for your interest in contributing to interrogate!

## Development Setup

1. Fork the repository and clone it locally.
2. Install Python 3.14+ and uv.
3. Install dependencies: `uv sync`
4. Run tests to ensure everything works: `uv run pytest`
5. Make your changes, add tests, and run all checks.

## Guidelines

- Use `uv run ruff format` to format code.
- Use type annotations for all functions.
- Write comprehensive unit tests for new features or bug fixes.
- Update the README.md if your changes affect usage or features.
- Keep commits atomic and descriptive.

## Submitting Changes

- Create a pull request with a clear title and description.
- Ensure all CI checks pass (pytest, ruff, ty).
- Reference any related issues.

## Reporting Issues

Use GitHub Issues for bugs or feature requests. Provide as much detail as possible, including steps to reproduce and your environment.
