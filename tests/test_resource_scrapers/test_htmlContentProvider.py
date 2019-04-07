from unittest import TestCase

from resource_scrapers.website_scraper import HtmlContentProvider


class TestHtmlContentProvider(TestCase):
    def setUp(self):
        self._html_provider = HtmlContentProvider()

    def test_get_html(self):
        content = self._html_provider.get_html('https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429')
        self.assertIsNotNone(content)
        self.assertGreater(len(content), 10)

