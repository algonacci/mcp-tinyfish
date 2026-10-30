import os
from typing import Optional
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP

load_dotenv()

mcp = FastMCP("TinyFish")
SEARCH_URL = "https://api.search.tinyfish.ai"
FETCH_URL = "https://api.fetch.tinyfish.ai"
MAX_RESULTS = 20
MAX_URLS = 10


def api_key() -> str:
    key = os.getenv("TINYFISH_API_KEY")
    if not key:
        raise ValueError("TINYFISH_API_KEY environment variable not set")
    return key


def error(exc: Exception) -> dict:
    if isinstance(exc, httpx.HTTPStatusError):
        return {"success": False, "status_code": exc.response.status_code,
                "error": f"TinyFish returned HTTP {exc.response.status_code}"}
    return {"success": False, "error": str(exc)}


@mcp.tool()
async def tinyfish_search(
    query: str,
    max_results: int = 10,
    include_domains: Optional[list[str]] = None,
    exclude_domains: Optional[list[str]] = None,
    location: str = "US",
    language: str = "en",
    ctx: Context = None,
) -> dict:
    """Search the web with TinyFish and return ranked links and snippets."""
    query = query.strip()
    if not query:
        return {"success": False, "error": "query must not be empty"}
    params = {"query": query, "location": location, "language": language}
    if include_domains:
        params["include_domains"] = ",".join(include_domains[:20])
    if exclude_domains:
        params["exclude_domains"] = ",".join(exclude_domains[:20])
    if ctx:
        ctx.info(f"Searching TinyFish for: {query}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(SEARCH_URL, params=params,
                                        headers={"X-API-Key": api_key()})
            response.raise_for_status()
            payload = response.json()
            limit = max(1, min(max_results, MAX_RESULTS))
            payload["results"] = payload.get("results", [])[:limit]
            return payload
    except (httpx.HTTPError, ValueError) as exc:
        return error(exc)


@mcp.tool()
async def tinyfish_fetch(
    urls: list[str],
    format: str = "markdown",
    cache_ttl_seconds: int = 3600,
    ctx: Context = None,
) -> dict:
    """Fetch and extract up to 10 public HTTP(S) URLs with TinyFish."""
    valid = [url for url in urls[:MAX_URLS]
             if urlparse(url).scheme in {"http", "https"} and urlparse(url).netloc]
    if not valid:
        return {"success": False, "error": "at least one public HTTP(S) URL is required"}
    if format not in {"markdown", "text", "html"}:
        return {"success": False, "error": "format must be markdown, text, or html"}
    if ctx:
        ctx.info(f"Fetching {len(valid)} URL(s) with TinyFish")
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(FETCH_URL, headers={"X-API-Key": api_key()}, json={
                "urls": valid, "format": format, "links": False, "image_links": False,
                "ttl": max(0, min(cache_ttl_seconds, 86400)), "per_url_timeout_ms": 30000,
            })
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        return error(exc)


if __name__ == "__main__":
    mcp.run()
