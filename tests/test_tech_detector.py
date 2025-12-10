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

    def test_html_meta_wordpress(self):
        headers = {}
        body = (
            '<html><head><meta name="generator" content="WordPress 5.8"></head></html>'
        )
        techs = detect_technologies(headers, body)
        assert {"name": "WordPress", "version": "5.8"} in techs

    def test_html_meta_joomla(self):
        headers = {}
        body = '<html><head><meta name="generator" content="Joomla! - Open Source Content Management"></head></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "Joomla", "version": None} in techs

    def test_html_meta_drupal(self):
        headers = {}
        body = '<html><head><meta name="generator" content="Drupal 9"></head></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "Drupal", "version": "9"} in techs

    def test_html_script_jquery(self):
        headers = {}
        body = '<html><script src="https://code.jquery.com/jquery-3.6.0.min.js"></script></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "jQuery", "version": "3.6.0"} in techs

    def test_html_script_react(self):
        headers = {}
        body = '<html><script src="https://unpkg.com/react@18.2.0/umd/react.production.min.js"></script></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "React", "version": "18.2.0"} in techs

    def test_html_script_vue(self):
        headers = {}
        body = '<html><script src="https://cdn.jsdelivr.net/npm/vue@3.2.0/dist/vue.global.js"></script></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "Vue.js", "version": "3.2.0"} in techs

    def test_html_script_angular(self):
        headers = {}
        body = '<html><script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.8.2/angular.min.js"></script></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "Angular", "version": "1.8.2"} in techs

    def test_html_script_alpine(self):
        headers = {}
        body = '<html><script src="https://cdn.jsdelivr.net/npm/alpinejs@3.10.0/dist/cdn.min.js"></script></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "Alpine.js", "version": "3.10.0"} in techs

    def test_html_script_bootstrap(self):
        headers = {}
        body = '<html><script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "Bootstrap", "version": "4.5.2"} in techs

    def test_html_google_analytics(self):
        headers = {}
        body = '<html><script src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"></script></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "Google Analytics", "version": None} in techs

    def test_html_facebook_pixel(self):
        headers = {}
        body = '<html><script src="https://connect.facebook.net/en_US/fbevents.js"></script></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "Facebook Pixel", "version": None} in techs

    def test_html_hotjar(self):
        headers = {}
        body = '<html><script src="https://static.hotjar.com/c/hotjar-123456.js?sv=6"></script></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "Hotjar", "version": None} in techs

    def test_html_shopify(self):
        headers = {}
        body = '<html><script src="https://cdn.shopify.com/shopifycloud/checkout-web/assets/checkout.js"></script></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "Shopify", "version": None} in techs

    def test_html_magento(self):
        headers = {}
        body = '<html><script src="https://magento.com/static/version1234567890/adminhtml/Magento/backend/en_US/requirejs/require.js"></script></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "Magento", "version": None} in techs

    def test_html_prestashop(self):
        headers = {}
        body = '<html><script src="https://prestashop.com/themes/default/js/prestashop.js"></script></html>'
        techs = detect_technologies(headers, body)
        assert {"name": "PrestaShop", "version": None} in techs

    def test_non_html_fallback(self):
        headers = {}
        body = '{"react": "library"}'
        techs = detect_technologies(headers, body)
        assert {"name": "React", "version": None} in techs

    def test_large_body_limit(self):
        headers = {}
        body = (
            '<html><head><meta name="generator" content="WordPress 5.8"></head></html>'
            + "x" * 200000
        )
        techs = detect_technologies(headers, body)
        assert {
            "name": "WordPress",
            "version": "5.8",
        } in techs  # Should still parse first 100KB

    def test_detect_from_robots_wordpress(self):
        headers = {}
        body = ""
        robots_txt = {"content": "User-agent: *\nDisallow: /wp-admin\n"}
        techs = detect_technologies(headers, body, robots_txt)
        assert {"name": "WordPress", "version": None} in techs

    def test_detect_from_robots_bitrix(self):
        headers = {}
        body = ""
        robots_txt = {"content": "User-agent: *\nDisallow: /bitrix/\n"}
        techs = detect_technologies(headers, body, robots_txt)
        assert {"name": "1C-Bitrix", "version": None} in techs

    def test_no_detect_from_robots_error(self):
        headers = {}
        body = ""
        robots_txt = {"error": "Not found"}
        techs = detect_technologies(headers, body, robots_txt)
        assert techs == []

    def test_no_detect_from_robots_missing_content(self):
        headers = {}
        body = ""
        robots_txt = {"disallowed": ["/"]}
        techs = detect_technologies(headers, body, robots_txt)
        assert techs == []
