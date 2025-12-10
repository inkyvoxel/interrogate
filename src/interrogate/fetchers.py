from typing import Dict, Any
import requests
import time
from .validators import validate_url
from .tech_detector import detect_technologies
from .robots import fetch_robots_txt
from .utils import retry_get


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

    # Fetch robots if needed for tech detection or output
    robots_info = None
    if include_robots or include_headers or include_body:
        robots_info = fetch_robots_txt(url)
        if (
            "crawl_delay" in robots_info
            and robots_info["crawl_delay"] is not None
            and robots_info["crawl_delay"] > 0
        ):
            time.sleep(robots_info["crawl_delay"])

    try:
        response = retry_get(
            url,
            headers={
                "User-Agent": "Interrogate/1.0 (+https://github.com/inkyvoxel/interrogate)"
            },
            timeout=10,
            allow_redirects=True,
            stream=True,
        )
        headers = dict(response.headers)
        status_code = response.status_code
        final_url = response.url
        # Cap body download at 150KB
        max_size = 150 * 1024
        content = b""
        for chunk in response.iter_content(chunk_size=1024):
            content += chunk
            if len(content) > max_size:
                content = content[:max_size]
                break
        # Attempt to decode as text
        try:
            body = content.decode("utf-8", errors="ignore")
        except UnicodeDecodeError:
            body = None  # Non-text content
        result = {
            "status_code": status_code,
            "final_url": final_url,
        }
        if include_headers or include_body:
            technologies = detect_technologies(headers, body, robots_info)
            result["technologies"] = technologies
        if include_headers:
            result["headers"] = headers
        if include_body:
            if status_code == 200 and body is not None:
                result["body_preview"] = body
            else:
                result["body_preview"] = None
        if include_robots:
            result["robots_txt"] = robots_info
        return result
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {e}")
