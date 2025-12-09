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
