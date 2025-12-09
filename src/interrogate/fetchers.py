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
        elif "nginx" in server:
            techs.append("Nginx")
        elif "iis" in server:
            techs.append("IIS")
    if "X-Powered-By" in headers:
        powered_by = headers["X-Powered-By"].lower()
        if "php" in powered_by:
            techs.append("PHP")
        elif "asp.net" in powered_by:
            techs.append("ASP.NET")
    # Body-based detection (simple regex)
    if re.search(r"<script[^>]*jquery", body, re.IGNORECASE):
        techs.append("jQuery")
    if re.search(r"wordpress", body, re.IGNORECASE):
        techs.append("WordPress")
    if re.search(r"bootstrap", body, re.IGNORECASE):
        techs.append("Bootstrap")
    return list(set(techs))  # Deduplicate
