"""Web text fetcher for Franquenstein external learning."""

from __future__ import annotations

import re
import urllib.request


def _strip_html(html: str) -> str:
    """Very lightweight HTML-to-text conversion."""
    # Remove scripts/styles
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.IGNORECASE)
    # Remove tags
    text = re.sub(r"<[^>]+>", " ", html)
    # Decode basic entities
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_web_text(url: str, timeout: float = 15.0) -> str:
    """Fetch a web page and return extracted text."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Franquenstein/1.0 (+local learning agent)"
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content_type = (resp.headers.get("Content-Type") or "").lower()
        raw = resp.read()

    text = raw.decode("utf-8", errors="replace")
    if "html" in content_type or "<html" in text.lower():
        return _strip_html(text)
    return text.strip()
