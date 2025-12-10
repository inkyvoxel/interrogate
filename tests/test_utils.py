import re
from unittest.mock import patch, MagicMock
from src.interrogate.utils import retry_get, extract_version


class TestRetryGet:
    @patch("src.interrogate.utils.requests.get")
    @patch("src.interrogate.utils.time.sleep")
    def test_retry_get_success_first_try(self, mock_sleep, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = retry_get("http://example.com", {"User-Agent": "test"})

        assert result == mock_response
        assert mock_get.call_count == 1
        mock_sleep.assert_not_called()

    @patch("src.interrogate.utils.requests.get")
    @patch("src.interrogate.utils.time.sleep")
    def test_retry_get_retry_on_429(self, mock_sleep, mock_get):
        mock_429_response = MagicMock()
        mock_429_response.status_code = 429
        mock_200_response = MagicMock()
        mock_200_response.status_code = 200
        mock_get.side_effect = [mock_429_response, mock_200_response]

        result = retry_get("http://example.com", {"User-Agent": "test"})

        assert result == mock_200_response
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once_with(2)

    @patch("src.interrogate.utils.requests.get")
    @patch("src.interrogate.utils.time.sleep")
    def test_retry_get_retry_on_503(self, mock_sleep, mock_get):
        mock_503_response = MagicMock()
        mock_503_response.status_code = 503
        mock_200_response = MagicMock()
        mock_200_response.status_code = 200
        mock_get.side_effect = [mock_503_response, mock_200_response]

        result = retry_get("http://example.com", {"User-Agent": "test"})

        assert result == mock_200_response
        assert mock_get.call_count == 2
        mock_sleep.assert_called_once_with(2)


class TestExtractVersion:
    def test_extract_version_with_group(self):
        pattern = re.compile(r"version (\d+(?:\.\d+)*)")
        match = pattern.search("Software version 1.2.3")
        result = extract_version(match)
        assert result == "1.2.3"

    def test_extract_version_no_group(self):
        pattern = re.compile(r"version")
        match = pattern.search("Software version")
        result = extract_version(match)
        assert result is None

    def test_extract_version_empty_group(self):
        pattern = re.compile(r"version (\d*)")
        match = pattern.search("Software version ")
        result = extract_version(match)
        assert result is None

    def test_extract_version_no_match(self):
        result = extract_version(None)
        assert result is None
