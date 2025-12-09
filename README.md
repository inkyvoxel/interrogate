# interrogate

Interrogate a URL for information.

## Installation

Clone the repository and install dependencies:

```bash
uv sync
```

## Usage

Run the CLI with a URL:

```bash
uv run interrogate --url https://example.com
# or for development: uv run main.py --url https://example.com
```

### Options

- `--headers`: Include full response headers in the output.
- `--body`: Include a preview of the response body in the output.
- `--robots`: Fetch and parse the site's robots.txt file.
- `--all`: Include all optional data (headers, body, and robots.txt).

### Examples

- Basic info: `uv run interrogate --url https://example.com`  
  Output (JSON):
  ```json
  {
    "status_code": 200,
    "final_url": "https://example.com"
  }
  ```

- With headers: `uv run interrogate --url https://example.com --headers`  
  Output includes `"headers": {...}` and `"technologies": [...]`.

- With body: `uv run interrogate --url https://example.com --body`  
  Output includes `"body_preview": "..."` and `"technologies": [...]`.

- With robots.txt: `uv run interrogate --url https://example.com --robots`  
  Output includes `"robots_txt": {"disallowed": [...], "sitemaps": [...], ...}`.

- All data: `uv run interrogate --url https://example.com --all`  
  Output includes all optional fields.

- Invalid URL: `uv run interrogate --url example.com`  
  Output: `Invalid URL: Missing protocol (e.g., http:// or https://)`

- Fetch error: `uv run interrogate --url https://invalid-domain.com`  
  Output: `Failed to fetch URL: ...`

## Development

- Run tests: `uv run pytest`
- Lint: `uv run ruff check`
- Format: `uv run ruff format`
- Type check: `uv run ty check`