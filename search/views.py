import logging
from urllib.parse import parse_qs, unquote, urlparse

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)

DDG_URL = "https://html.duckduckgo.com/html/"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 10


def _clean_ddg_url(href):
    """DDG wraps result links via /l/?uddg=<encoded>. Unwrap it."""
    if not href:
        return ""
    if href.startswith("//"):
        href = "https:" + href
    parsed = urlparse(href)
    if parsed.netloc.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
        target = parse_qs(parsed.query).get("uddg", [""])[0]
        return unquote(target)
    return href


def get_search_result(query):
    """Scrape DuckDuckGo HTML for the given query.

    Returns a list of {title, url, snippet} dicts. Empty list on any failure.
    """
    if not query:
        return []

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://duckduckgo.com/",
    }

    try:
        response = requests.post(
            DDG_URL,
            data={"q": query, "kl": "us-en"},
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("DuckDuckGo request failed: %s", exc)
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    results = []

    for elm in soup.select("div.result, div.web-result"):
        anchor = elm.select_one("a.result__a")
        if not anchor:
            continue
        title = anchor.get_text(strip=True)
        url = _clean_ddg_url(anchor.get("href", ""))
        if not title or not url:
            continue

        snippet_tag = elm.select_one(".result__snippet")
        snippet = (
            snippet_tag.get_text(" ", strip=True) if snippet_tag else ""
        )

        results.append({"title": title, "url": url, "snippet": snippet})

    return results


def search(request):
    query = request.GET.get("search", "").strip()
    context = {"query": query, "results": []}
    if query:
        context["results"] = get_search_result(query)
    return render(request, "search/search.html", context)


def api(request):
    query = request.GET.get("search", "").strip()
    return JsonResponse(
        {
            "query": query,
            "results": get_search_result(query) if query else [],
        }
    )
