import pytest
from unittest.mock import patch, MagicMock
from requests import RequestException
from src.interrogate.fetchers import (
    fetch_url_info,
    detect_technologies,
    fetch_robots_txt,
)


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

        with patch("src.interrogate.fetchers.requests.get", side_effect=mock_get):
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

        with patch("src.interrogate.fetchers.requests.get", side_effect=mock_get):
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

        with patch("src.interrogate.fetchers.requests.get", side_effect=mock_get):
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


class TestDetectTechnologies:
    def test_detect_from_headers(self):
        headers = {"Server": "Apache/2.4", "X-Powered-By": "ASP.NET"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "Apache" in techs
        assert "ASP.NET" in techs

    def test_detect_from_body(self):
        headers = {}
        body = "<script src='jquery.js'></script> bootstrap WordPress"
        techs = detect_technologies(headers, body)
        assert "jQuery" in techs
        assert "Bootstrap" in techs
        assert "WordPress" in techs

    def test_no_detection(self):
        headers = {}
        body = "plain text"
        techs = detect_technologies(headers, body)
        assert techs == []

    def test_deduplication(self):
        headers = {"Server": "nginx", "X-Powered-By": "PHP"}
        body = "jquery jquery"
        techs = detect_technologies(headers, body)
        assert len(techs) == len(set(techs))  # No duplicates

    def test_detect_new_servers(self):
        # Test LiteSpeed
        headers = {"Server": "LiteSpeed"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "LiteSpeed" in techs

        # Test Caddy
        headers = {"Server": "Caddy"}
        techs = detect_technologies(headers, body)
        assert "Caddy" in techs

        # Test Tomcat
        headers = {"Server": "Apache Tomcat"}
        techs = detect_technologies(headers, body)
        assert "Tomcat" in techs

    def test_detect_new_runtimes(self):
        # Test Node.js
        headers = {"X-Powered-By": "Node.js"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "Node.js" in techs

        # Test Python
        headers = {"X-Powered-By": "Python/3.9"}
        techs = detect_technologies(headers, body)
        assert "Python" in techs

    def test_detect_wordpress_from_generator(self):
        headers = {"X-Generator": "WordPress 5.8"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "WordPress" in techs

    def test_detect_new_body_technologies(self):
        headers = {}
        # Test React
        body = "react component"
        techs = detect_technologies(headers, body)
        assert "React" in techs

        # Test Vue.js
        body = "vue app"
        techs = detect_technologies(headers, body)
        assert "Vue.js" in techs

        # Test Angular
        body = "angular framework"
        techs = detect_technologies(headers, body)
        assert "Angular" in techs

        # Test Django
        body = "django powered"
        techs = detect_technologies(headers, body)
        assert "Django" in techs

        # Test Flask
        body = "flask application"
        techs = detect_technologies(headers, body)
        assert "Flask" in techs

    def test_detect_cdn_cloudflare(self):
        headers = {"CF-RAY": "1234567890abcdef"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "Cloudflare" in techs

    def test_detect_cdn_akamai(self):
        headers = {"X-Akamai-Transformed": "9 - 0 pmb=mRUM,1"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "Akamai" in techs

    def test_detect_cdn_aws_cloudfront(self):
        headers = {"X-Amz-Cf-Id": "abc123"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "AWS CloudFront" in techs

    def test_detect_cdn_fastly(self):
        headers = {"X-Served-By": "cache-iad-kiad7000123-IAD"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "Fastly" in techs

    def test_detect_cdn_azure(self):
        headers = {"X-Azure-Ref": "12345"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "Azure CDN" in techs

    def test_detect_cdn_google_cloud(self):
        headers = {"Server": "Google Frontend"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "Google Cloud CDN" in techs

    def test_detect_cdn_bunny(self):
        headers = {"Server": "BunnyCDN"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "Bunny CDN" in techs

    def test_detect_cdn_imperva(self):
        headers = {"X-Iinfo": "5-123456-123456"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "Imperva" in techs

    def test_detect_cdn_keycdn(self):
        headers = {"Server": "KeyCDN"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "KeyCDN" in techs

    def test_detect_cdn_stackpath(self):
        headers = {"Server": "StackPath"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "StackPath" in techs

    def test_detect_cdn_cdn77(self):
        headers = {"Server": "CDN77"}
        body = ""
        techs = detect_technologies(headers, body)
        assert "CDN77" in techs


class TestFetchRobotsTxt:
    @patch("src.interrogate.fetchers.requests.get")
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

    @patch("src.interrogate.fetchers.requests.get")
    def test_robots_404(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = fetch_robots_txt("https://example.com")

        assert "error" in result
        assert "not found" in result["error"]
