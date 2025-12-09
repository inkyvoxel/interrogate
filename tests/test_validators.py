"""Tests for URL validators."""

import pytest

from src.interrogate.validators import validate_url


class TestValidateUrl:
    """Test cases for validate_url function."""

    def test_valid_http_url(self):
        """Test a valid HTTP URL."""
        validate_url("http://example.com")
        # Should not raise

    def test_valid_https_url(self):
        """Test a valid HTTPS URL."""
        validate_url("https://example.com/path?query=value")
        # Should not raise

    def test_missing_protocol(self):
        """Test URL missing protocol."""
        with pytest.raises(ValueError, match="Missing protocol"):
            validate_url("example.com")

    def test_missing_netloc(self):
        """Test URL missing network location."""
        with pytest.raises(ValueError, match="Missing domain or network location"):
            validate_url("http://")

    def test_empty_url(self):
        """Test empty URL."""
        with pytest.raises(ValueError, match="Missing protocol"):
            validate_url("")

    def test_invalid_scheme_only(self):
        """Test URL with only invalid scheme."""
        with pytest.raises(ValueError, match="Missing domain or network location"):
            validate_url("http://")
