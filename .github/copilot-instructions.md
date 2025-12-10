# Copilot Instructions for interrogate

## Project Overview
This is a Python package project for interrogating URLs, using modern tooling for dependency management and environment isolation. The package provides a CLI tool to fetch and analyze URL information, including HTTP status, headers, detected technologies, and body preview.

## Architecture
- **Package Structure**: Code organized under `src/interrogate/` as a proper Python package for distribution and reusability
- **Entry Points**:
  - `main.py`: Development wrapper that imports from the package
  - `src/interrogate/__main__.py`: Main CLI logic with argument parsing
  - `pyproject.toml` defines `interrogate` console script pointing to `interrogate.__main__:main`
- **Core Components**:
  - `validators.py`: URL validation utilities using `urllib.parse`
  - `fetchers.py`: HTTP fetching and orchestrating technology detection and robots.txt parsing
  - `tech_detector.py`: Technology detection via headers and body regex patterns
  - `robots.py`: Robots.txt fetching and parsing using `requests` and `urljoin`
- **Data Flow**: CLI arguments `--url` (required), `--headers`, `--body`, `--robots`, `--all` → `validate_url()` → `fetch_url_info()` with include_* flags → JSON output with status_code, final_url, and conditionally headers, technologies, body_preview, robots_txt; errors as ValueError messages
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
- **Lint code**: `uv run ruff check --fix` (uses `ruff` from dev dependencies)
- **Format code**: `uv run ruff format`
- **Type check**: `uv run ty check` (uses `ty` from dev dependencies)
- **Environment setup**: `mise install` to install tools and create venv, `uv sync` to install packages

## Conventions
- Use `uv` for all package operations (install, sync, etc.) and script execution (`uv run`) - do not use pip
- Use `ruff` for linting (`uv run ruff check --fix`) and formatting (`uv run ruff format`)
- Use `ty` for type checking (`uv run ty check`)
- Write typed Python code with type annotations for better type safety and IDE support
- Project configuration in `pyproject.toml` following PEP 621
- Version management via mise for reproducible environments
- Tests in `tests/` directory, mirroring source structure (e.g., `test_validators.py` for `validators.py`, `test_fetchers.py` for `fetchers.py`)
- URL validation/fetching raises `ValueError` with descriptive messages (e.g., "Invalid URL: Missing protocol", "Failed to fetch URL: ...")
- Testing: Use pytest with class-based test cases, mock HTTP requests with `unittest.mock.patch` on `requests.get`

## File Structure
- `main.py`: Development entry point importing from package
- `src/interrogate/__init__.py`: Package init with version
- `src/interrogate/__main__.py`: CLI argument parsing and main logic
- `src/interrogate/validators.py`: URL validation functions
- `src/interrogate/fetchers.py`: URL fetching orchestration
- `src/interrogate/tech_detector.py`: Technology detection logic
- `src/interrogate/robots.py`: Robots.txt handling
- `tests/test_validators.py`: Unit tests for validators
- `tests/test_fetchers.py`: Unit tests for fetchers with mocked requests
- `tests/test_tech_detector.py`: Unit tests for tech detection
- `tests/test_robots.py`: Unit tests for robots parsing
- `pyproject.toml`: Project metadata, dependencies (requests), scripts, and tool configs
- `mise.toml`: Tool configuration for uv
- `.python-version`: Python version pin (implied by mise)

## Integration Points
- HTTP requests via `requests` library with timeout and redirect handling
- Technology detection: Regex patterns on response body for frameworks (jQuery, WordPress, Bootstrap, React, Vue.js, Angular, Django, Flask), header parsing for servers (Apache/Nginx/IIS/LiteSpeed/Caddy/Tomcat), runtimes (PHP/ASP.NET/Node.js/Python), and CDNs (Cloudflare, Akamai, AWS CloudFront, Fastly, Azure CDN, Google Cloud CDN, Bunny CDN, Imperva, KeyCDN, StackPath, CDN77)
- Robots.txt fetching and parsing: Construct robots.txt URL with `urljoin`, fetch with `requests`, parse for disallowed paths, sitemaps, crawl-delay, user-agents