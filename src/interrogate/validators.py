"""URL validation utilities."""

from urllib.parse import urlparse


def validate_url(url: str) -> None:
    """Validate the URL syntax.

    Args:
        url: The URL string to validate.

    Raises:
        ValueError: If the URL is invalid.
    """
    parsed = urlparse(url)
    if not parsed.scheme:
        raise ValueError("Invalid URL: Missing protocol (e.g., http:// or https://)")
    if not parsed.netloc:
        raise ValueError("Invalid URL: Missing domain or network location")
