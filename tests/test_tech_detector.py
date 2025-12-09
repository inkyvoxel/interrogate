from src.interrogate.tech_detector import detect_technologies


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
