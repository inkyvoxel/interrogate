import re
from typing import Dict, Any
import requests
from .validators import validate_url


def fetch_url_info(url: str) -> Dict[str, Any]:
    """
    Fetches URL info via GET request, including headers, status, final URL, and tech detection.
    Raises ValueError on fetch errors.
    """
    validate_url(url)  # Reuse existing validation
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        headers = dict(response.headers)
        status_code = response.status_code
        final_url = response.url
        body = response.text[:1000]  # Limit to first 1000 chars for analysis
        technologies = detect_technologies(headers, body)
        return {
            "status_code": status_code,
            "final_url": final_url,
            "headers": headers,
            "technologies": technologies,
            "body_preview": body[:200],  # Short preview
        }
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {e}")


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
