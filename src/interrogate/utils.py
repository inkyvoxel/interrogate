import re
import time
from typing import Dict, Optional

import requests


def retry_get(
    url: str,
    headers: Dict[str, str],
    timeout: int = 10,
    allow_redirects: bool = True,
    stream: bool = False,
) -> requests.Response:
    """
    Perform a GET request with retry on 429 or 503 status codes.
    Sleeps for 2 seconds before retrying once.
    """
    response = requests.get(
        url,
        headers=headers,
        timeout=timeout,
        allow_redirects=allow_redirects,
        stream=stream,
    )
    if response.status_code in [429, 503]:
        time.sleep(2)
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            allow_redirects=allow_redirects,
            stream=stream,
        )
    return response


def extract_version(match: Optional[re.Match[str]]) -> Optional[str]:
    """
    Extract version from a regex match, returning group 1 if present and not empty.
    """
    if match is None:
        return None
    if match.groups() and match.group(1):
        return match.group(1)
    return None
