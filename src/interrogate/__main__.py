"""Command-line interface for interrogate."""

import argparse
import sys

from .validators import validate_url


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Interrogate CLI app")
    parser.add_argument("--url", required=True, help="The URL to interrogate")
    args = parser.parse_args()

    try:
        validate_url(args.url)
    except ValueError as e:
        print(e)
        sys.exit(1)

    print(f"URL: {args.url}")


if __name__ == "__main__":
    main()
