# interrogate

Interrogate a URL for information, including HTTP status, headers, technologies, body preview, and robots.txt parsing.

## Features

- **URL Validation**: Ensures valid HTTP/HTTPS URLs.
- **HTTP Fetching**: Retrieves status code, final URL after redirects, and optional headers/body.
- **Technology Detection**: Identifies servers (e.g., Apache, Nginx), runtimes (e.g., PHP, Node.js), frameworks (e.g., WordPress, React), and CDNs (e.g., Cloudflare) via regex and HTML parsing.
- **Robots.txt Parsing**: Fetches and parses robots.txt for disallowed paths, sitemaps, crawl-delay, and user-agents.
- **Retry Logic**: Handles rate limits (429) and server errors (503) with exponential backoff.
- **JSON Output**: Structured output for easy parsing.

## Installation

For development, clone and install:

```bash
git clone https://github.com/inkyvoxel/interrogate.git
cd interrogate
uv sync
```

## Usage

```bash
uv run main.py --url https://example.com --all
```

### Options

- `--url URL`: The URL to interrogate (required).
- `--headers`: Include full response headers and detected technologies.
- `--body`: Include a preview of the response body (up to 150KB) and detected technologies.
- `--robots`: Fetch and parse the site's robots.txt.
- `--all`: Include all optional data (headers, body, and robots.txt).
- `--help`: Show help message and exit.

### Output Format

The tool outputs JSON to stdout.

**Basic Output** (always included):
```json
{
  "status_code": 200,
  "final_url": "https://example.com"
}
```

**With `--headers`**:
```json
{
  "status_code": 200,
  "final_url": "https://example.com",
  "headers": {
    "content-type": "text/html",
    "server": "nginx"
  },
  "technologies": [
    {"name": "Nginx", "version": null},
    {"name": "WordPress", "version": "6.0"}
  ]
}
```

**With `--body`**:
```json
{
  "status_code": 200,
  "final_url": "https://example.com",
  "body": "<!DOCTYPE html><html><head><title>Example</title></head><body>...</body></html>",
  "technologies": [
    {"name": "jQuery", "version": "3.6.0"}
  ]
}
```

**With `--robots`**:
```json
{
  "status_code": 200,
  "final_url": "https://example.com",
  "robots_txt": {
    "disallowed": ["/admin/", "/private/"],
    "sitemaps": ["https://example.com/sitemap.xml"],
    "crawl_delay": 1,
    "user_agents": ["*"]
  }
}
```

**Technologies Detected**: Servers (Apache, Nginx, IIS, LiteSpeed, Caddy, Tomcat), Runtimes (PHP, ASP.NET, Node.js, Python), Frameworks (WordPress, React, Vue.js, Angular, Django, Flask, Joomla, Drupal), CDNs (Cloudflare, Akamai, AWS CloudFront), and more.

### Examples

- Basic: `uv run main.py --url https://example.com`
- Headers: `uv run main.py --url https://example.com --headers`
- Body: `uv run main.py --url https://example.com --body`
- Robots: `uv run main.py --url https://example.com --robots`
- All: `uv run main.py --url https://example.com --all`

Errors are printed to stderr, e.g., `Invalid URL: Missing protocol` or `Failed to fetch URL: Connection timeout`.

## Development

- Run tests: `uv run pytest`
- Lint: `uv run ruff check --fix`
- Format: `uv run ruff format`
- Type check: `uv run ty check`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License. See [LICENSE](LICENSE) for details.