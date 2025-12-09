from typing import Dict, Any
import requests
from .validators import validate_url
from .tech_detector import detect_technologies
from .robots import fetch_robots_txt


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
