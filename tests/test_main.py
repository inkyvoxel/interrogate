"""Tests for the CLI main module."""

import pytest
import sys
from unittest.mock import patch

from interrogate.__main__ import main


def test_help(capsys):
    """Test that --help prints help and exits."""
    with patch.object(sys, "argv", ["main.py", "--help"]):
        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower()
        assert "help" in captured.out.lower()
        assert "url" in captured.out.lower()
