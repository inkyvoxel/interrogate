# Copilot Instructions for interrogate

## Project Overview
Python package for interrogating URLs via CLI, fetching HTTP status, headers, technologies, body preview, and robots.txt parsing.

## Architecture
- **Package Structure**: Code in `src/interrogate/` for distribution; `main.py` for development imports from package.
- **Entry Points**: `__main__.py` for CLI argument parsing; `pyproject.toml` defines `interrogate` script.
- **Core Components**:
  - `validators.py`: URL validation with `urllib.parse`.
  - `fetchers.py`: Orchestrates fetching, tech detection, robots parsing using `requests`.
  - `tech_detector.py`: Detects technologies via regex on headers/body and BeautifulSoup HTML parsing (e.g., jQuery, WordPress, React).
  - `robots.py`: Fetches/parses robots.txt with `urljoin` and `requests`.
  - `utils.py`: Retry logic for GET requests on 429/503.
- **Data Flow**: CLI `--url` (required), `--headers`, `--body`, `--robots`, `--all` → `validate_url()` → `fetch_url_info()` with include_* flags → JSON output (status_code, final_url, conditional headers/technologies/body_preview/robots_txt); errors as ValueError.

## Development Environment
- Python >=3.14 (via `pyproject.toml`).
- Tooling: `mise.toml` configures `uv` with auto venv creation (`.venv/`).
- Dependencies: `requests`, `beautifulsoup4`, `lxml`, `tenacity` (core); `ruff`, `ty`, `pytest` (dev).

## Key Workflows
- **Run CLI (dev)**: `uv run main.py --url https://example.com --all`
- **Run CLI (installed)**: `uv pip install .` then `interrogate --url https://example.com --all`
- **Add deps**: Edit `pyproject.toml` dependencies, `uv sync`
- **Add dev deps**: `uv add --dev <package>` (e.g., `uv add --dev ruff`)
- **Run tests**: `uv run pytest` (testpaths=["tests"])
- **Lint**: `uv run ruff check --fix`
- **Format**: `uv run ruff format`
- **Type check**: `uv run ty check`
- **Setup**: `mise install` (tools/venv), `uv sync` (packages)

## Conventions
- Use `uv` for package ops and script execution; avoid `pip`.
- Use `ruff` for linting/formatting, `ty` for type checking.
- Write typed Python with annotations.
- Config in `pyproject.toml` (PEP 621).
- Version management via `mise`.
- Tests in `tests/` mirroring `src/` (e.g., `test_fetchers.py`); mock `requests.get` with `unittest.mock.patch`.
- Errors: Raise `ValueError` with messages (e.g., "Invalid URL: Missing protocol").
- Tech detection: Regex patterns for frameworks (jQuery, Bootstrap), servers (Apache, Nginx), runtimes (PHP, Node.js), CDNs (Cloudflare, Akamai).
- Robots: Construct URL with `urljoin`, parse for disallowed/sitemaps/crawl-delay/user-agents.

## File Structure
- `main.py`: Dev entry importing from package.
- `src/interrogate/__init__.py`: Package init with version.
- `src/interrogate/__main__.py`: CLI logic.
- `src/interrogate/validators.py`: URL validation.
- `src/interrogate/fetchers.py`: Fetching orchestration.
- `src/interrogate/tech_detector.py`: Tech detection.
- `src/interrogate/robots.py`: Robots handling.
- `src/interrogate/utils.py`: Utilities like retry_get.
- `tests/`: Unit tests with mocked requests.
- `pyproject.toml`: Metadata, deps, scripts, tool configs.
- `mise.toml`: uv config.
- `.python-version`: Version pin.