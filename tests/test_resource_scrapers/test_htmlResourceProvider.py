from unittest import TestCase

from resource_scrapers.website_scraper import HtmlResourceProvider


class TestHtmlResourceProvider(TestCase):
    def setUp(self):
        self._html_provider = HtmlResourceProvider()

    def test_get_html(self):
        content = self._html_provider.get_html('https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429')
        self.assertIsNotNone(content)
        self.assertGreater(len(content), 10)

