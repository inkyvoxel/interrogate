import re
from typing import Dict


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
    # CDN detection
    if (
        "CF-RAY" in headers
        or "CF-IPCountry" in headers
        or ("Server" in headers and "cloudflare" in headers["Server"].lower())
    ):
        techs.append("Cloudflare")
    if (
        "X-Akamai-Transformed" in headers
        or ("Server" in headers and "akamai" in headers["Server"].lower())
        or ("X-Cache" in headers and "AkamaiGHost" in headers["X-Cache"])
    ):
        techs.append("Akamai")
    if (
        "X-Amz-Cf-Id" in headers
        or ("Via" in headers and "cloudfront.net" in headers["Via"])
        or ("X-Cache" in headers and "cloudfront" in headers["X-Cache"].lower())
    ):
        techs.append("AWS CloudFront")
    if (
        "X-Served-By" in headers
        or ("X-Cache" in headers and headers["X-Cache"].upper() in ["MISS", "HIT"])
        or ("Server" in headers and "fastly" in headers["Server"].lower())
    ):
        techs.append("Fastly")
    if (
        "X-Azure-Ref" in headers
        or "X-Azure-RequestChain" in headers
        or ("Server" in headers and "azurecdn" in headers["Server"].lower())
    ):
        techs.append("Azure CDN")
    if ("X-Cache" in headers and headers["X-Cache"].upper() in ["HIT", "MISS"]) or (
        "Server" in headers and "google frontend" in headers["Server"].lower()
    ):
        techs.append("Google Cloud CDN")
    if (
        "Server" in headers and "bunnycdn" in headers["Server"].lower()
    ) or "X-Bunny-Id" in headers:
        techs.append("Bunny CDN")
    if "X-Iinfo" in headers:
        techs.append("Imperva")
    if (
        "Server" in headers and "keycdn" in headers["Server"].lower()
    ) or "X-Edge-Location" in headers:
        techs.append("KeyCDN")
    if (
        "Server" in headers and "stackpath" in headers["Server"].lower()
    ) or "X-HW" in headers:
        techs.append("StackPath")
    if (
        "Server" in headers and "cdn77" in headers["Server"].lower()
    ) or "X-Cache-Status" in headers:
        techs.append("CDN77")
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
