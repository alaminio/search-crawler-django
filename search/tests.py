from unittest.mock import patch

from django.test import TestCase


BING_HTML = """
<html><body>
<ol id="b_results">
  <li class="b_algo">
    <h2><a href="https://example.com/one">First result</a></h2>
    <div class="b_caption"><p>Description one.</p></div>
  </li>
  <li class="b_algo">
    <h2><a href="https://example.com/two">Second result</a></h2>
    <div class="b_caption"><p>Description two.</p></div>
  </li>
</ol>
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

    @patch("search.views.requests.get")
    def test_search_parses_bing_html(self, mock_get):
        mock_get.return_value = FakeResponse(BING_HTML.encode("utf-8"))
        response = self.client.get("/?search=hello")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First result")
        self.assertContains(response, "Second result")
        self.assertContains(response, "Description one.")

    @patch("search.views.requests.get")
    def test_search_handles_network_error(self, mock_get):
        import requests

        mock_get.side_effect = requests.RequestException("boom")
        response = self.client.get("/?search=hello")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No results found")


class ApiViewTests(TestCase):
    def test_empty_query_returns_empty_results(self):
        response = self.client.get("/api/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"query": "", "results": []})

    @patch("search.views.requests.get")
    def test_api_returns_parsed_results(self, mock_get):
        mock_get.return_value = FakeResponse(BING_HTML.encode("utf-8"))
        response = self.client.get("/api/?search=hello")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["query"], "hello")
        self.assertEqual(len(payload["results"]), 2)
        self.assertEqual(payload["results"][0]["title"], "First result")
        self.assertEqual(payload["results"][0]["url"], "https://example.com/one")
        self.assertEqual(payload["results"][0]["snippet"], "Description one.")
