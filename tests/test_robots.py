from unittest.mock import patch, MagicMock
from src.interrogate.robots import fetch_robots_txt


class TestFetchRobotsTxt:
    @patch("src.interrogate.robots.requests.get")
    def test_robots_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "user-agent: *\ndisallow: /private"
        mock_get.return_value = mock_response

        result = fetch_robots_txt("https://example.com")

        assert "disallowed" in result
        assert "/private" in result["disallowed"]
        assert "sitemaps" in result
        assert result["sitemaps"] == []
        assert "user_agents" in result
        assert "*" in result["user_agents"]
        assert "raw" in result

    @patch("src.interrogate.robots.requests.get")
    def test_robots_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = fetch_robots_txt("https://example.com")

        assert "error" in result
        assert "not found" in result["error"]

    @patch("src.interrogate.robots.requests.get")
    @patch("src.interrogate.robots.time.sleep")
    def test_robots_retry_on_429(self, mock_sleep, mock_get):
        mock_429_response = MagicMock()
        mock_429_response.status_code = 429
        mock_200_response = MagicMock()
        mock_200_response.status_code = 200
        mock_200_response.text = "user-agent: *\ndisallow: /private"
        mock_get.side_effect = [mock_429_response, mock_200_response]

        result = fetch_robots_txt("https://example.com")

        assert mock_sleep.called
        assert "disallowed" in result
