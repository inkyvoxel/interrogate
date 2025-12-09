import pytest
from unittest.mock import patch, MagicMock
from requests import RequestException
from src.interrogate.fetchers import fetch_url_info


class TestFetchUrlInfo:
    @patch("src.interrogate.fetchers.requests.get")
    def test_successful_fetch(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.headers = {"Server": "nginx", "X-Powered-By": "PHP"}
        mock_response.text = (
            "<html><script src='jquery.js'></script>WordPress site</html>"
        )
        mock_get.return_value = mock_response

        result = fetch_url_info(
            "https://example.com", include_headers=True, include_body=True
        )

        assert result["status_code"] == 200
        assert result["final_url"] == "https://example.com"
        assert "Server" in result["headers"]
        assert "Nginx" in result["technologies"]
        assert "PHP" in result["technologies"]
        assert "jQuery" in result["technologies"]
        assert "WordPress" in result["technologies"]
        assert (
            result["body_preview"]
            == "<html><script src='jquery.js'></script>WordPress site</html>"
        )

    @patch("src.interrogate.fetchers.requests.get")
    def test_fetch_error(self, mock_get):
        mock_get.side_effect = RequestException("Connection error")

        with pytest.raises(ValueError, match="Failed to fetch URL"):
            fetch_url_info("https://example.com")


class TestFetchUrlInfoFlags:
    @patch("src.interrogate.fetchers.requests.get")
    def test_include_headers(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.headers = {"Server": "nginx"}
        mock_response.text = "body"
        mock_get.return_value = mock_response

        result = fetch_url_info("https://example.com", include_headers=True)

        assert "headers" in result
        assert "technologies" in result
        assert "body_preview" not in result
        assert "robots_txt" not in result

    @patch("src.interrogate.fetchers.requests.get")
    def test_include_body(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.headers = {}
        mock_response.text = "body content"
        mock_get.return_value = mock_response

        result = fetch_url_info("https://example.com", include_body=True)

        assert "body_preview" in result
        assert "technologies" in result
        assert "headers" not in result
        assert "robots_txt" not in result

    def test_include_robots_success(self):
        # Mock for main URL and robots.txt
        def mock_get(url, **kwargs):
            if url == "https://example.com":
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.url = "https://example.com"
                mock_resp.headers = {}
                mock_resp.text = ""
                return mock_resp
            elif url == "https://example.com/robots.txt":
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.text = "User-agent: *\nDisallow: /private\nSitemap: https://example.com/sitemap.xml"
                return mock_resp
            else:
                raise RequestException("Not found")

        with (
            patch("src.interrogate.fetchers.requests.get", side_effect=mock_get),
            patch("src.interrogate.robots.requests.get", side_effect=mock_get),
        ):
            result = fetch_url_info("https://example.com", include_robots=True)

        assert "robots_txt" in result
        robots = result["robots_txt"]
        assert "disallowed" in robots
        assert "/private" in robots["disallowed"]
        assert "sitemaps" in robots
        assert "https://example.com/sitemap.xml" in robots["sitemaps"]
        assert "user_agents" in robots
        assert "*" in robots["user_agents"]

    def test_include_robots_404(self):
        def mock_get(url, **kwargs):
            if url == "https://example.com":
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.url = "https://example.com"
                mock_resp.headers = {}
                mock_resp.text = ""
                return mock_resp
            elif url == "https://example.com/robots.txt":
                mock_resp = MagicMock()
                mock_resp.status_code = 404
                return mock_resp
            else:
                raise RequestException("Not found")

        with (
            patch("src.interrogate.fetchers.requests.get", side_effect=mock_get),
            patch("src.interrogate.robots.requests.get", side_effect=mock_get),
        ):
            result = fetch_url_info("https://example.com", include_robots=True)

        assert "robots_txt" in result
        assert "error" in result["robots_txt"]
        assert "not found (status 404)" in result["robots_txt"]["error"]

    def test_include_robots_malformed(self):
        def mock_get(url, **kwargs):
            if url == "https://example.com":
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.url = "https://example.com"
                mock_resp.headers = {}
                mock_resp.text = ""
                return mock_resp
            elif url == "https://example.com/robots.txt":
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.text = "Invalid robots.txt content"
                return mock_resp
            else:
                raise RequestException("Not found")

        with (
            patch("src.interrogate.fetchers.requests.get", side_effect=mock_get),
            patch("src.interrogate.robots.requests.get", side_effect=mock_get),
        ):
            result = fetch_url_info("https://example.com", include_robots=True)

        assert "robots_txt" in result
        robots = result["robots_txt"]
        # Even malformed, it should parse what it can
        assert "disallowed" in robots or "error" in robots

    @patch("src.interrogate.fetchers.requests.get")
    def test_include_all(self, mock_get):
        # For simplicity, mock only main URL, assume robots fetch fails
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.url = "https://example.com"
        mock_response.headers = {"Server": "nginx"}
        mock_response.text = "body"
        mock_get.return_value = mock_response

        result = fetch_url_info(
            "https://example.com",
            include_headers=True,
            include_body=True,
            include_robots=True,
        )

        assert "headers" in result
        assert "body_preview" in result
        assert "technologies" in result
        assert "robots_txt" in result  # Even if error, it should be present
