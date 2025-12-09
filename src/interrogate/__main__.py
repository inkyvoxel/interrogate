"""Command-line interface for interrogate."""

import argparse
import json
import sys

from .fetchers import fetch_url_info


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Interrogate CLI app")
    parser.add_argument("--url", required=True, help="The URL to interrogate")
    parser.add_argument(
        "--headers", action="store_true", help="Include response headers in output"
    )
    parser.add_argument(
        "--body", action="store_true", help="Include body preview in output"
    )
    parser.add_argument(
        "--robots", action="store_true", help="Fetch and parse robots.txt"
    )
    parser.add_argument("--all", action="store_true", help="Include all optional data")
    args = parser.parse_args()

    include_headers = args.headers or args.all
    include_body = args.body or args.all
    include_robots = args.robots or args.all

    try:
        result = fetch_url_info(
            args.url,
            include_headers=include_headers,
            include_body=include_body,
            include_robots=include_robots,
        )
        print(json.dumps(result, indent=2))
    except ValueError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
