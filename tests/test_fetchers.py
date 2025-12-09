import pytest
from unittest.mock import patch, MagicMock
from requests import RequestException
from src.interrogate.fetchers import fetch_url_info, detect_technologies


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

        result = fetch_url_info("https://example.com")

        assert result["status_code"] == 200
        assert result["final_url"] == "https://example.com"
        assert "Server" in result["headers"]
        assert "Nginx" in result["technologies"]
        assert "PHP" in result["technologies"]
        assert "jQuery" in result["technologies"]
        assert "WordPress" in result["technologies"]
        assert (
            result["body_preview"]
            == "<html><script src='jquery.js'></script>WordPress site</html>"[:200]
        )

    @patch("src.interrogate.fetchers.requests.get")
    def test_fetch_error(self, mock_get):
        mock_get.side_effect = RequestException("Connection error")

        with pytest.raises(ValueError, match="Failed to fetch URL"):
            fetch_url_info("https://example.com")


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
