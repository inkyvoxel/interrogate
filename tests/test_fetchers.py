import pytest
from unittest.mock import patch, MagicMock
from requests import RequestException
from src.interrogate.fetchers import fetch_url_info


class TestFetchUrlInfo:
    @patch("src.interrogate.fetchers.requests.get")
    def test_successful_fetch(self, mock_get):
        # Mock robots.txt response
        mock_robots_response = MagicMock()
        mock_robots_response.status_code = 200
        mock_robots_response.text = "User-agent: *\nDisallow: /admin\n"
        # Mock main response
        mock_main_response = MagicMock()
        mock_main_response.status_code = 200
        mock_main_response.url = "https://example.com"
        mock_main_response.headers = {"Server": "nginx", "X-Powered-By": "PHP"}
        body_text = "<html><script src='jquery.js'></script>WordPress site</html>"
        mock_main_response.iter_content.return_value = iter([body_text.encode("utf-8")])
        mock_get.side_effect = [mock_robots_response, mock_main_response]

        result = fetch_url_info(
            "https://example.com", include_headers=True, include_body=True
        )

        assert result["status_code"] == 200
        assert result["final_url"] == "https://example.com"
        assert "Server" in result["headers"]
        assert {"name": "Nginx", "version": None} in result["technologies"]
        assert {"name": "PHP", "version": None} in result["technologies"]
        assert {"name": "jQuery", "version": None} in result["technologies"]
        assert {"name": "WordPress", "version": None} in result["technologies"]
        assert result["body_preview"] == body_text

    @patch("src.interrogate.fetchers.requests.get")
    def test_fetch_error(self, mock_get):
        mock_get.side_effect = RequestException("Connection error")

        with pytest.raises(ValueError, match="Failed to fetch URL"):
            fetch_url_info("https://example.com")

    @patch("src.interrogate.fetchers.requests.get")
    def test_non_200_response(self, mock_get):
        # Mock robots
        mock_robots_response = MagicMock()
        mock_robots_response.status_code = 200
        mock_robots_response.text = "User-agent: *\nDisallow: /admin\n"
        # Mock main 404
        mock_main_response = MagicMock()
        mock_main_response.status_code = 404
        mock_main_response.url = "https://example.com"
        mock_main_response.headers = {}
        mock_main_response.iter_content.return_value = iter([b"Not found"])
        mock_get.side_effect = [mock_robots_response, mock_main_response]

        result = fetch_url_info("https://example.com", include_body=True)

        assert result["status_code"] == 404
        assert result["body_preview"] is None

    @patch("src.interrogate.fetchers.requests.get")
    @patch("src.interrogate.fetchers.time.sleep")
    def test_retry_on_429(self, mock_sleep, mock_get):
        # Mock robots
        mock_robots_response = MagicMock()
        mock_robots_response.status_code = 200
        mock_robots_response.text = "User-agent: *\nDisallow: /admin\n"
        # Mock main 429 then 200
        mock_429_response = MagicMock()
        mock_429_response.status_code = 429
        mock_200_response = MagicMock()
        mock_200_response.status_code = 200
        mock_200_response.url = "https://example.com"
        mock_200_response.headers = {}
        mock_200_response.iter_content.return_value = iter([b"OK"])
        mock_get.side_effect = [
            mock_robots_response,
            mock_429_response,
            mock_200_response,
        ]

        result = fetch_url_info("https://example.com", include_body=True)

        assert mock_sleep.called
        assert result["status_code"] == 200
        assert result["body_preview"] == "OK"

    @patch("src.interrogate.fetchers.requests.get")
    @patch("src.interrogate.fetchers.time.sleep")
    def test_crawl_delay_sleep(self, mock_sleep, mock_get):
        # Mock robots with crawl-delay
        mock_robots_response = MagicMock()
        mock_robots_response.status_code = 200
        mock_robots_response.text = "User-agent: *\nDisallow: /admin\nCrawl-delay: 5\n"
        # Mock main
        mock_main_response = MagicMock()
        mock_main_response.status_code = 200
        mock_main_response.url = "https://example.com"
        mock_main_response.headers = {}
        mock_main_response.iter_content.return_value = iter([b"OK"])
        mock_get.side_effect = [mock_robots_response, mock_main_response]

        result = fetch_url_info("https://example.com", include_body=True)

        mock_sleep.assert_called_with(5.0)
        assert result["status_code"] == 200


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
