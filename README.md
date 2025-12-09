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

### Examples

- Valid URL: `uv run interrogate --url https://example.com`  
  Output (JSON):
  ```json
  {
    "status_code": 200,
    "final_url": "https://example.com",
    "headers": {
      "Content-Type": "text/html",
      "Server": "nginx"
    },
    "technologies": ["Nginx"],
    "body_preview": "<!doctype html><html..."
  }
  ```

- Invalid URL: `uv run interrogate --url example.com`  
  Output: `Invalid URL: Missing protocol (e.g., http:// or https://)`

- Fetch error: `uv run interrogate --url https://invalid-domain.com`  
  Output: `Failed to fetch URL: ...`

## Development

- Run tests: `uv run pytest`
- Lint: `uv run ruff check`
- Format: `uv run ruff format`
- Type check: `uv run ty`