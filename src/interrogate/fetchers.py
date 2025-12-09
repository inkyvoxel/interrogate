import re
from typing import Dict, Any
import requests
from urllib.parse import urljoin
from .validators import validate_url


def fetch_url_info(
    url: str,
    include_headers: bool = False,
    include_body: bool = False,
    include_robots: bool = False,
) -> Dict[str, Any]:
    """
    Fetches URL info via GET request, conditionally including headers, body, and robots.txt.
    Raises ValueError on fetch errors.
    """
    validate_url(url)  # Reuse existing validation
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        headers = dict(response.headers)
        status_code = response.status_code
        final_url = response.url
        body = response.text
        result = {
            "status_code": status_code,
            "final_url": final_url,
        }
        if include_headers or include_body:
            technologies = detect_technologies(headers, body)
            result["technologies"] = technologies
        if include_headers:
            result["headers"] = headers
        if include_body:
            result["body_preview"] = body
        if include_robots:
            robots_info = fetch_robots_txt(url)
            result["robots_txt"] = robots_info
        return result
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {e}")


def fetch_robots_txt(url: str) -> Dict[str, Any]:
    """
    Fetches and parses robots.txt for the given URL.
    Returns a dict with disallowed, sitemaps, crawl_delay, user_agents, raw, or {"error": message} on failure.
    """
    try:
        robots_url = urljoin(url, "/robots.txt")
        response = requests.get(robots_url, timeout=10, allow_redirects=True)
        if response.status_code != 200:
            return {"error": f"robots.txt not found (status {response.status_code})"}
        raw = response.text
        lines = raw.splitlines()
        user_agents = []
        disallowed = []
        sitemaps = []
        crawl_delay = None
        for line in lines:
            line = line.strip().lower()
            if line.startswith("user-agent:"):
                useragent = line[11:].strip()
                user_agents.append(useragent)
            elif line.startswith("disallow:"):
                path = line[9:].strip()
                if path:
                    disallowed.append(path)
            elif line.startswith("crawl-delay:"):
                delay_str = line[12:].strip()
                try:
                    crawl_delay = float(delay_str)
                except ValueError:
                    pass
            elif line.startswith("sitemap:"):
                sitemap = line[8:].strip()
                sitemaps.append(sitemap)
        return {
            "disallowed": list(set(disallowed)),
            "sitemaps": sitemaps,
            "crawl_delay": crawl_delay,
            "user_agents": list(set(user_agents)),
            "raw": raw,
        }
    except requests.RequestException as e:
        return {"error": f"Failed to fetch robots.txt: {e}"}
    except Exception as e:
        return {"error": f"Failed to parse robots.txt: {e}"}


def detect_technologies(headers: Dict[str, str], body: str) -> list[str]:
    """
    Simple tech detection based on headers and body patterns.
    """
    techs = []
    # Header-based detection
    if "Server" in headers:
        server = headers["Server"].lower()
        if "apache" in server:
            techs.append("Apache")
        if "nginx" in server:
            techs.append("Nginx")
        if "iis" in server:
            techs.append("IIS")
        if "litespeed" in server:
            techs.append("LiteSpeed")
        if "caddy" in server:
            techs.append("Caddy")
        if "tomcat" in server:
            techs.append("Tomcat")
    if "X-Powered-By" in headers:
        powered_by = headers["X-Powered-By"].lower()
        if "php" in powered_by:
            techs.append("PHP")
        elif "asp.net" in powered_by:
            techs.append("ASP.NET")
        elif "node.js" in powered_by:
            techs.append("Node.js")
        elif "python" in powered_by:
            techs.append("Python")
    if "X-Generator" in headers:
        generator = headers["X-Generator"].lower()
        if "wordpress" in generator:
            techs.append("WordPress")
    # Body-based detection (simple regex)
    if re.search(r"<script[^>]*jquery", body, re.IGNORECASE):
        techs.append("jQuery")
    if re.search(r"wordpress", body, re.IGNORECASE):
        techs.append("WordPress")
    if re.search(r"bootstrap", body, re.IGNORECASE):
        techs.append("Bootstrap")
    if re.search(r"react", body, re.IGNORECASE):
        techs.append("React")
    if re.search(r"vue", body, re.IGNORECASE):
        techs.append("Vue.js")
    if re.search(r"angular", body, re.IGNORECASE):
        techs.append("Angular")
    if re.search(r"django", body, re.IGNORECASE):
        techs.append("Django")
    if re.search(r"flask", body, re.IGNORECASE):
        techs.append("Flask")
    return list(set(techs))  # Deduplicate
