from unittest import TestCase

from resource_scrapers.website_scraper import ImageScraper



class TestImageScraper(TestCase):
    def setUp(self) -> None:
        url: str = 'https://www.emag.pl/'
        self.image_extractor = ImageScraper(url)

    def test_pull_images_from_html_references(self):

        self.image_extractor.pull_images_from_html_references()

    def test_url_to_folder_name(self):
        test_cases = [
            ('http://www.url.com/asd', 'www.url.comasd'),
            ('https://www.url.com/asd', 'www.url.comasd')
        ]

        for url, expected in test_cases:
            with self.subTest(name=str(url)):
                self.assertEqual(url_to_folder_name(url), expected)
