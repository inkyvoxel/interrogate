# interrogate

Interrogate a URL for information.

## Installation

Clone the repository and install dependencies:

```bash
git clone <repository-url>
cd interrogate
uv sync
```

## Usage

Run the CLI with a URL:

```bash
uv run interrogate --url https://example.com
# or for development: uv run main.py --url https://example.com
```

### Examples

- Valid URL: `uv run interrogate --url http://example.com`  
  Output: `URL: http://example.com`

- Invalid URL (missing protocol): `uv run interrogate --url example.com`  
  Output: `Invalid URL: Missing protocol (e.g., http:// or https://)`

- Invalid URL (missing domain): `uv run interrogate --url http://`  
  Output: `Invalid URL: Missing domain or network location`

## Development

- Run tests: `uv run pytest`
- Lint: `uv run ruff check`
- Format: `uv run ruff format`
- Type check: `uv run ty`