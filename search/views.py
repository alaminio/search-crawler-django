import logging

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.shortcuts import render

logger = logging.getLogger(__name__)

BING_URL = "https://www.bing.com/search"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 8


def get_search_result(query):
    """Scrape Bing search results.

    Returns a list of {title, url, snippet} dicts. Empty list on any failure.
    """
    if not query:
        return []

    try:
        response = requests.get(
            BING_URL,
            params={"q": query},
            headers={
                "User-Agent": USER_AGENT,
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Bing request failed: %s", exc)
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    container = soup.find("ol", id="b_results") or soup
    items = container.find_all("li", class_="b_algo")

    results = []
    for elm in items:
        anchor = elm.find("a", href=True)
        if not anchor:
            continue
        title = anchor.get_text(strip=True)
        url = anchor.get("href", "")
        if not title or not url:
            continue

        snippet_tag = elm.find("p")
        snippet = snippet_tag.get_text(" ", strip=True) if snippet_tag else ""

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
