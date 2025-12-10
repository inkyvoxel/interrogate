import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from .utils import extract_version


def detect_technologies(
    headers: Dict[str, str],
    body: Optional[str],
    robots_txt: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Optional[str]]]:
    """
    Detect technologies from headers and body with version extraction.
    Returns list of dicts with 'name' and optional 'version'.
    """
    techs = []

    # Define regex patterns for servers with version extraction
    server_patterns = {
        "Tomcat": re.compile(r"\bApache Tomcat(?:/(\d+(?:\.\d+)*))?", re.IGNORECASE),
        "Apache": re.compile(r"\bApache(?:/(\d+(?:\.\d+)*))?", re.IGNORECASE),
        "Nginx": re.compile(r"\bnginx(?:/(\d+(?:\.\d+)*))?", re.IGNORECASE),
        "IIS": re.compile(r"\bMicrosoft-IIS(?:/(\d+(?:\.\d+)*))?", re.IGNORECASE),
        "LiteSpeed": re.compile(r"\bLiteSpeed(?:/(\d+(?:\.\d+)*))?", re.IGNORECASE),
        "Caddy": re.compile(r"\bCaddy(?:/(\d+(?:\.\d+)*))?", re.IGNORECASE),
    }

    # Check Server header
    if "Server" in headers:
        server = headers["Server"]
        for name, pattern in server_patterns.items():
            match = pattern.search(server)
            if match:
                techs.append({"name": name, "version": extract_version(match)})
                break  # Assume only one server

    # Define patterns for X-Powered-By
    powered_by_patterns = {
        "PHP": re.compile(r"\bPHP(?:/(\d+(?:\.\d+)*))?", re.IGNORECASE),
        "ASP.NET": re.compile(r"\bASP\.NET(?:/(\d+(?:\.\d+)*))?", re.IGNORECASE),
        "Node.js": re.compile(r"\bNode\.js(?:/(\d+(?:\.\d+)*))?", re.IGNORECASE),
        "Python": re.compile(r"\bPython(?:/(\d+(?:\.\d+)*))?", re.IGNORECASE),
    }

    if "X-Powered-By" in headers:
        powered_by = headers["X-Powered-By"]
        for name, pattern in powered_by_patterns.items():
            match = pattern.search(powered_by)
            if match:
                techs.append({"name": name, "version": extract_version(match)})
                break  # Assume one primary runtime

    # X-Generator for WordPress
    if "X-Generator" in headers:
        generator = headers["X-Generator"]
        wp_match = re.search(
            r"\bWordPress(?: (\d+(?:\.\d+)*))?", generator, re.IGNORECASE
        )
        if wp_match:
            techs.append({"name": "WordPress", "version": extract_version(wp_match)})

    # CDN detection with prioritization
    # Order: specific headers first, then server strings
    cdn_checks = [
        (
            "Fastly",
            [
                lambda h: "X-Served-By" in h,
                lambda h: "X-Cache" in h and "fastly" in h["X-Cache"].lower(),
                lambda h: "Server" in h
                and re.search(r"\bfastly\b", h["Server"], re.IGNORECASE),
            ],
        ),
        (
            "Cloudflare",
            [
                lambda h: "CF-RAY" in h,
                lambda h: "CF-IPCountry" in h,
                lambda h: "Server" in h
                and re.search(r"\bcloudflare\b", h["Server"], re.IGNORECASE),
            ],
        ),
        (
            "Akamai",
            [
                lambda h: "X-Akamai-Transformed" in h,
                lambda h: "X-Cache" in h and "AkamaiGHost" in h["X-Cache"],
                lambda h: "Server" in h
                and re.search(r"\bakamai\b", h["Server"], re.IGNORECASE),
            ],
        ),
        (
            "AWS CloudFront",
            [
                lambda h: "X-Amz-Cf-Id" in h,
                lambda h: "Via" in h and "cloudfront.net" in h["Via"],
                lambda h: "X-Cache" in h and "cloudfront" in h["X-Cache"].lower(),
            ],
        ),
        (
            "Azure CDN",
            [
                lambda h: "X-Azure-Ref" in h,
                lambda h: "X-Azure-RequestChain" in h,
                lambda h: "Server" in h
                and re.search(r"\bazurecdn\b", h["Server"], re.IGNORECASE),
            ],
        ),
        (
            "Google Cloud CDN",
            [
                lambda h: "Server" in h
                and re.search(r"\bgoogle frontend\b", h["Server"], re.IGNORECASE),
                lambda h: "X-Cache" in h and h["X-Cache"].upper() in ["HIT", "MISS"],
            ],
        ),
        (
            "Bunny CDN",
            [
                lambda h: "X-Bunny-Id" in h,
                lambda h: "Server" in h
                and re.search(r"\bbunnycdn\b", h["Server"], re.IGNORECASE),
            ],
        ),
        (
            "Imperva",
            [
                lambda h: "X-Iinfo" in h,
            ],
        ),
        (
            "KeyCDN",
            [
                lambda h: "X-Edge-Location" in h,
                lambda h: "Server" in h
                and re.search(r"\bkeycdn\b", h["Server"], re.IGNORECASE),
            ],
        ),
        (
            "StackPath",
            [
                lambda h: "X-HW" in h,
                lambda h: "Server" in h
                and re.search(r"\bstackpath\b", h["Server"], re.IGNORECASE),
            ],
        ),
        (
            "CDN77",
            [
                lambda h: "X-Cache-Status" in h,
                lambda h: "Server" in h
                and re.search(r"\bcdn77\b", h["Server"], re.IGNORECASE),
            ],
        ),
    ]

    for cdn_name, checks in cdn_checks:
        for check in checks:
            if check(headers):
                techs.append({"name": cdn_name, "version": None})
                break  # Found this CDN, skip to next

    # HTML-based detection with BeautifulSoup
    if body:
        is_html = re.search(r"<!DOCTYPE|<html", body[:1000], re.IGNORECASE)
        if is_html:
            limited_body = body[: 100 * 1024]  # Limit to 100KB
            soup = BeautifulSoup(limited_body, "lxml")

            # Meta tags for CMSs
            for meta in soup.find_all("meta"):
                name = str(meta.get("name", "")).lower()
                content = str(meta.get("content", "")).lower()
                if name == "generator":
                    if "wordpress" in content:
                        version_match = re.search(r"(\d+(?:\.\d+)*)", content)
                        if version_match:
                            techs.append(
                                {
                                    "name": "WordPress",
                                    "version": extract_version(version_match),
                                }
                            )
                    elif "joomla" in content:
                        version_match = re.search(r"(\d+(?:\.\d+)*)", content)
                        if version_match:
                            techs.append(
                                {
                                    "name": "Joomla",
                                    "version": extract_version(version_match),
                                }
                            )
                    elif "drupal" in content:
                        version_match = re.search(r"(\d+(?:\.\d+)*)", content)
                        if version_match:
                            techs.append(
                                {
                                    "name": "Drupal",
                                    "version": extract_version(version_match),
                                }
                            )
                    elif "wix" in content:
                        techs.append({"name": "Wix", "version": None})
                    elif "squarespace" in content:
                        techs.append({"name": "Squarespace", "version": None})

            # Script sources (limit to 30)
            scripts = soup.find_all("script", src=True)[:30]
            for script in scripts:
                src = str(script["src"]).lower()
                if "jquery" in src:
                    version_match = re.search(r"jquery-(\d+(?:\.\d+)*)", src)
                    if version_match:
                        techs.append(
                            {
                                "name": "jQuery",
                                "version": extract_version(version_match),
                            }
                        )
                elif "react" in src or "__next_data__" in limited_body:
                    version_match = re.search(
                        r"react(?:\.|@)(\d+(?:\.\d+)*)", src
                    ) or re.search(r'"version":"(\d+(?:\.\d+)*)"', limited_body)
                    if version_match:
                        techs.append(
                            {
                                "name": "React",
                                "version": extract_version(version_match),
                            }
                        )
                elif "vue" in src:
                    version_match = re.search(r"vue(?:\.|@)(\d+(?:\.\d+)*)", src)
                    if version_match:
                        techs.append(
                            {
                                "name": "Vue.js",
                                "version": extract_version(version_match),
                            }
                        )
                elif "angular" in src:
                    version_match = re.search(
                        r"angularjs/(\d+(?:\.\d+)*)", src
                    ) or re.search(r"angular(?:\.|@)(\d+(?:\.\d+)*)", src)
                    if version_match:
                        techs.append(
                            {
                                "name": "Angular",
                                "version": extract_version(version_match),
                            }
                        )
                elif "alpine" in src:
                    version_match = re.search(
                        r"alpinejs@(\d+(?:\.\d+)*)", src
                    ) or re.search(r"alpine(?:\.|@)(\d+(?:\.\d+)*)", src)
                    if version_match:
                        techs.append(
                            {
                                "name": "Alpine.js",
                                "version": extract_version(version_match),
                            }
                        )
                elif "bootstrap" in src:
                    version_match = re.search(
                        r"bootstrap/(\d+(?:\.\d+)*)", src
                    ) or re.search(r"bootstrap(?:\.|@)(\d+(?:\.\d+)*)", src)
                    if version_match:
                        techs.append(
                            {
                                "name": "Bootstrap",
                                "version": extract_version(version_match),
                            }
                        )
                elif (
                    "googletagmanager" in src or "analytics.js" in src or "gtag" in src
                ):
                    techs.append({"name": "Google Analytics", "version": None})
                elif "facebook" in src and "fbevents" in src:
                    techs.append({"name": "Facebook Pixel", "version": None})
                elif "hotjar" in src:
                    techs.append({"name": "Hotjar", "version": None})
                elif "shopify" in src:
                    techs.append({"name": "Shopify", "version": None})
                elif "magento" in src:
                    techs.append({"name": "Magento", "version": None})
                elif "prestashop" in src:
                    techs.append({"name": "PrestaShop", "version": None})

    # Body-based detection (expanded with regex fallbacks)
    if body:
        body_patterns = {
            "jQuery": re.compile(r"\bjquery\b", re.IGNORECASE),
            "WordPress": re.compile(r"\bwordpress\b", re.IGNORECASE),
            "Bootstrap": re.compile(r"\bbootstrap\b", re.IGNORECASE),
            "React": re.compile(r"\breact\b", re.IGNORECASE),
            "Vue.js": re.compile(r"\bvue\b", re.IGNORECASE),
            "Angular": re.compile(r"\bangular\b", re.IGNORECASE),
            "Django": re.compile(r"\bdjango\b", re.IGNORECASE),
            "Flask": re.compile(r"\bflask\b", re.IGNORECASE),
            "Joomla": re.compile(r"\bjoomla\b", re.IGNORECASE),
            "Drupal": re.compile(r"\bdrupal\b", re.IGNORECASE),
            "Wix": re.compile(r"\bwix\b", re.IGNORECASE),
            "Squarespace": re.compile(r"\bsquarespace\b", re.IGNORECASE),
            "Alpine.js": re.compile(r"\balpine\b", re.IGNORECASE),
            "Google Analytics": re.compile(
                r"\bgoogle.*analytics\b|\bgtag\b", re.IGNORECASE
            ),
            "Facebook Pixel": re.compile(r"\bfacebook.*pixel\b", re.IGNORECASE),
            "Hotjar": re.compile(r"\bhotjar\b", re.IGNORECASE),
            "Shopify": re.compile(r"\bshopify\b", re.IGNORECASE),
            "Magento": re.compile(r"\bmagento\b", re.IGNORECASE),
            "PrestaShop": re.compile(r"\bprestashop\b", re.IGNORECASE),
        }

        for name, pattern in body_patterns.items():
            if pattern.search(body):
                techs.append({"name": name, "version": None})

    # Robots.txt-based detection
    if robots_txt and "content" in robots_txt:
        content = robots_txt["content"]
        robots_patterns = {
            "WordPress": re.compile(r"disallow:\s*/wp-admin", re.IGNORECASE),
            "1C-Bitrix": re.compile(r"disallow:\s*/bitrix/", re.IGNORECASE),
        }
        for name, pattern in robots_patterns.items():
            if pattern.search(content):
                techs.append({"name": name, "version": None})

    # Deduplicate by name
    seen = set()
    unique_techs = []
    for tech in techs:
        if tech["name"] not in seen:
            seen.add(tech["name"])
            unique_techs.append(tech)

    return unique_techs
