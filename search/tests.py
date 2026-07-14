from unittest.mock import patch

from django.test import TestCase


DDG_HTML = """
<html><body>
<div class="results">
  <div class="result results_links results_links_deep web-result">
    <div class="result__body">
      <h2 class="result__title">
        <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fone&amp;rut=x">First result</a>
      </h2>
      <a class="result__snippet" href="https://example.com/one">Description one.</a>
    </div>
  </div>
  <div class="result results_links results_links_deep web-result">
    <div class="result__body">
      <h2 class="result__title">
        <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Ftwo&amp;rut=x">Second result</a>
      </h2>
      <a class="result__snippet" href="https://example.com/two">Description two.</a>
    </div>
  </div>
</div>
</body></html>
"""


class FakeResponse:
    def __init__(self, content, status_code=200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")


class SearchViewTests(TestCase):
    def test_empty_query_renders_landing(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Search the web")

    @patch("search.views.requests.post")
    def test_search_parses_html(self, mock_post):
        mock_post.return_value = FakeResponse(DDG_HTML.encode("utf-8"))
        response = self.client.get("/?search=hello")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First result")
        self.assertContains(response, "Second result")
        self.assertContains(response, "Description one.")

    @patch("search.views.requests.post")
    def test_search_handles_network_error(self, mock_post):
        import requests

        mock_post.side_effect = requests.RequestException("boom")
        response = self.client.get("/?search=hello")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No results found")


class ApiViewTests(TestCase):
    def test_empty_query_returns_empty_results(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"query": "", "results": []})

    @patch("search.views.requests.post")
    def test_api_returns_parsed_results(self, mock_post):
        mock_post.return_value = FakeResponse(DDG_HTML.encode("utf-8"))
        response = self.client.get("/api/?search=hello")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["query"], "hello")
        self.assertEqual(len(payload["results"]), 2)
        self.assertEqual(payload["results"][0]["title"], "First result")
        self.assertEqual(payload["results"][0]["url"], "https://example.com/one")
        self.assertEqual(payload["results"][0]["snippet"], "Description one.")
