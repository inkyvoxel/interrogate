from typing import Dict, Any
import requests
from urllib.parse import urljoin
from .utils import retry_get


def fetch_robots_txt(url: str) -> Dict[str, Any]:
    """
    Fetches and parses robots.txt for the given URL.
    Returns a dict with disallowed, sitemaps, crawl_delay, user_agents, raw, or {"error": message} on failure.
    """
    try:
        robots_url = urljoin(url, "/robots.txt")
        response = retry_get(
            robots_url,
            headers={
                "User-Agent": "Interrogate/1.0 (+https://github.com/inkyvoxel/interrogate)"
            },
            timeout=10,
            allow_redirects=True,
        )
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
