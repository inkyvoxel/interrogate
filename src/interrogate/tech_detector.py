import re
from typing import Dict, List, Optional


def detect_technologies(
    headers: Dict[str, str], body: str
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
                techs.append({"name": name, "version": match.group(1)})
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
                version = match.group(1) if match.groups() and match.group(1) else None
                techs.append({"name": name, "version": version})
                break  # Assume one primary runtime

    # X-Generator for WordPress
    if "X-Generator" in headers:
        generator = headers["X-Generator"]
        wp_match = re.search(
            r"\bWordPress(?: (\d+(?:\.\d+)*))?", generator, re.IGNORECASE
        )
        if wp_match:
            version = wp_match.group(1) if wp_match.group(1) else None
            techs.append({"name": "WordPress", "version": version})

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

    # Body-based detection (keep simple for now, as focus is headers)
    body_patterns = {
        "jQuery": re.compile(r"\bjquery\b", re.IGNORECASE),
        "WordPress": re.compile(r"\bwordpress\b", re.IGNORECASE),
        "Bootstrap": re.compile(r"\bbootstrap\b", re.IGNORECASE),
        "React": re.compile(r"\breact\b", re.IGNORECASE),
        "Vue.js": re.compile(r"\bvue\b", re.IGNORECASE),
        "Angular": re.compile(r"\bangular\b", re.IGNORECASE),
        "Django": re.compile(r"\bdjango\b", re.IGNORECASE),
        "Flask": re.compile(r"\bflask\b", re.IGNORECASE),
    }

    for name, pattern in body_patterns.items():
        if pattern.search(body):
            techs.append({"name": name, "version": None})

    # Deduplicate by name
    seen = set()
    unique_techs = []
    for tech in techs:
        if tech["name"] not in seen:
            seen.add(tech["name"])
            unique_techs.append(tech)

    return unique_techs
