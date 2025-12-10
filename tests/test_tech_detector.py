from src.interrogate.tech_detector import detect_technologies


class TestDetectTechnologies:
    def test_detect_from_headers(self):
        headers = {"Server": "Apache/2.4", "X-Powered-By": "ASP.NET"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Apache", "version": "2.4"} in techs
        assert {"name": "ASP.NET", "version": None} in techs

    def test_detect_from_body(self):
        headers = {}
        body = "<script src='jquery.js'></script> bootstrap WordPress"
        techs = detect_technologies(headers, body)
        names = [t["name"] for t in techs]
        assert "jQuery" in names
        assert "Bootstrap" in names
        assert "WordPress" in names

    def test_no_detection(self):
        headers = {}
        body = "plain text"
        techs = detect_technologies(headers, body)
        assert techs == []

    def test_deduplication(self):
        headers = {"Server": "nginx", "X-Powered-By": "PHP"}
        body = "jquery jquery"
        techs = detect_technologies(headers, body)
        names = [t["name"] for t in techs]
        assert len(names) == len(set(names))  # No duplicates

    def test_detect_new_servers(self):
        # Test LiteSpeed
        headers = {"Server": "LiteSpeed"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "LiteSpeed", "version": None} in techs

        # Test Caddy
        headers = {"Server": "Caddy"}
        techs = detect_technologies(headers, body)
        assert {"name": "Caddy", "version": None} in techs

        # Test Tomcat
        headers = {"Server": "Apache Tomcat"}
        techs = detect_technologies(headers, body)
        assert {"name": "Tomcat", "version": None} in techs

    def test_detect_new_runtimes(self):
        # Test Node.js
        headers = {"X-Powered-By": "Node.js"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Node.js", "version": None} in techs

        # Test Python
        headers = {"X-Powered-By": "Python/3.9"}
        techs = detect_technologies(headers, body)
        assert {"name": "Python", "version": "3.9"} in techs

    def test_detect_wordpress_from_generator(self):
        headers = {"X-Generator": "WordPress 5.8"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "WordPress", "version": "5.8"} in techs

    def test_detect_new_body_technologies(self):
        headers = {}
        # Test React
        body = "react component"
        techs = detect_technologies(headers, body)
        assert {"name": "React", "version": None} in techs

        # Test Vue.js
        body = "vue app"
        techs = detect_technologies(headers, body)
        assert {"name": "Vue.js", "version": None} in techs

        # Test Angular
        body = "angular framework"
        techs = detect_technologies(headers, body)
        assert {"name": "Angular", "version": None} in techs

        # Test Django
        body = "django powered"
        techs = detect_technologies(headers, body)
        assert {"name": "Django", "version": None} in techs

        # Test Flask
        body = "flask application"
        techs = detect_technologies(headers, body)
        assert {"name": "Flask", "version": None} in techs

    def test_detect_cdn_cloudflare(self):
        headers = {"CF-RAY": "1234567890abcdef"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Cloudflare", "version": None} in techs

    def test_detect_cdn_akamai(self):
        headers = {"X-Akamai-Transformed": "9 - 0 pmb=mRUM,1"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Akamai", "version": None} in techs

    def test_detect_cdn_aws_cloudfront(self):
        headers = {"X-Amz-Cf-Id": "abc123"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "AWS CloudFront", "version": None} in techs

    def test_detect_cdn_fastly(self):
        headers = {"X-Served-By": "cache-iad-kiad7000123-IAD"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Fastly", "version": None} in techs

    def test_detect_cdn_azure(self):
        headers = {"X-Azure-Ref": "12345"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Azure CDN", "version": None} in techs

    def test_detect_cdn_google_cloud(self):
        headers = {"Server": "Google Frontend"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Google Cloud CDN", "version": None} in techs

    def test_detect_cdn_bunny(self):
        headers = {"Server": "BunnyCDN"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Bunny CDN", "version": None} in techs

    def test_detect_cdn_imperva(self):
        headers = {"X-Iinfo": "5-123456-123456"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Imperva", "version": None} in techs

    def test_detect_cdn_keycdn(self):
        headers = {"Server": "KeyCDN"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "KeyCDN", "version": None} in techs

    def test_detect_cdn_stackpath(self):
        headers = {"Server": "StackPath"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "StackPath", "version": None} in techs

    def test_detect_cdn_cdn77(self):
        headers = {"Server": "CDN77"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "CDN77", "version": None} in techs

    # Real-world header examples
    def test_real_world_apache(self):
        headers = {"Server": "Apache/2.4.29 (Ubuntu)"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Apache", "version": "2.4.29"} in techs

    def test_real_world_nginx(self):
        headers = {"Server": "nginx/1.18.0"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Nginx", "version": "1.18.0"} in techs

    def test_real_world_iis(self):
        headers = {"Server": "Microsoft-IIS/10.0"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "IIS", "version": "10.0"} in techs

    def test_real_world_litespeed(self):
        headers = {"Server": "LiteSpeed/5.4.12"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "LiteSpeed", "version": "5.4.12"} in techs

    def test_real_world_caddy(self):
        headers = {"Server": "Caddy/2.4.6"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Caddy", "version": "2.4.6"} in techs

    def test_real_world_tomcat(self):
        headers = {"Server": "Apache Tomcat/9.0.50"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Tomcat", "version": "9.0.50"} in techs

    def test_real_world_php(self):
        headers = {"X-Powered-By": "PHP/8.0.3"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "PHP", "version": "8.0.3"} in techs

    def test_real_world_asp_net(self):
        headers = {"X-Powered-By": "ASP.NET/4.8"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "ASP.NET", "version": "4.8"} in techs

    def test_real_world_node_js(self):
        headers = {"X-Powered-By": "Node.js/14.17.0"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Node.js", "version": "14.17.0"} in techs

    def test_real_world_python(self):
        headers = {"X-Powered-By": "Python/3.9.5"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Python", "version": "3.9.5"} in techs

    def test_real_world_wordpress(self):
        headers = {"X-Generator": "WordPress 5.8.1"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "WordPress", "version": "5.8.1"} in techs

    def test_real_world_cloudflare(self):
        headers = {"CF-RAY": "6b6b6b6b6b6b6b6b-LAX", "Server": "cloudflare"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Cloudflare", "version": None} in techs

    def test_real_world_akamai(self):
        headers = {"X-Akamai-Transformed": "9 - 0 pmb=mRUM,1", "Server": "AkamaiGHost"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Akamai", "version": None} in techs

    def test_real_world_aws_cloudfront(self):
        headers = {
            "X-Amz-Cf-Id": "abc123def456",
            "Via": "1.1 abc123.cloudfront.net (CloudFront)",
        }
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "AWS CloudFront", "version": None} in techs

    def test_real_world_fastly(self):
        headers = {"X-Served-By": "cache-lax1234-LAX", "X-Cache": "HIT"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Fastly", "version": None} in techs

    def test_real_world_azure_cdn(self):
        headers = {"X-Azure-Ref": "20211201T123456Z-abc123", "Server": "AzureCDN"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Azure CDN", "version": None} in techs

    def test_real_world_google_cloud_cdn(self):
        headers = {"Server": "Google Frontend", "X-Cache": "HIT"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Google Cloud CDN", "version": None} in techs

    def test_real_world_bunny_cdn(self):
        headers = {"X-Bunny-Id": "123456", "Server": "BunnyCDN-TX1-123"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Bunny CDN", "version": None} in techs

    def test_real_world_imperva(self):
        headers = {"X-Iinfo": "5-123456-123456"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "Imperva", "version": None} in techs

    def test_real_world_keycdn(self):
        headers = {"X-Edge-Location": "us-west-1", "Server": "KeyCDN"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "KeyCDN", "version": None} in techs

    def test_real_world_stackpath(self):
        headers = {"X-HW": "123456", "Server": "StackPath"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "StackPath", "version": None} in techs

    def test_real_world_cdn77(self):
        headers = {"X-Cache-Status": "HIT", "Server": "CDN77-Turbo"}
        body = ""
        techs = detect_technologies(headers, body)
        assert {"name": "CDN77", "version": None} in techs
