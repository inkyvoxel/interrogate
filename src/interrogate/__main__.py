"""Command-line interface for interrogate."""

import argparse
import json
import sys

from .fetchers import fetch_url_info


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Interrogate CLI app")
    parser.add_argument("--url", required=True, help="The URL to interrogate")
    args = parser.parse_args()

    try:
        result = fetch_url_info(args.url)
        print(json.dumps(result, indent=2))
    except ValueError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
