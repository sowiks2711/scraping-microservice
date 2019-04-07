from typing import List
from unittest import TestCase

from resource_scrapers.website_scraper import TextExtractor


class TestTextExtractor(TestCase):
    def setUp(self) -> None:
        self.text_extractor: TestTextExtractor = TextExtractor()
        with open('hello-world.html') as f:
            self.html_content: str = f.read()

    def test_extract_text_from_html(self):
        expected_lines: List[str] = ['Title', 'My First Heading', 'My first paragraph.', 'This is a link', 'Click me',
                                     'Coffee', 'Tea', 'Milk', 'This is a', 'paragraph with a line break.',
                                     'First name:', 'Last name:']
        expected = '\n'.join(expected_lines)

        extracted_text = self.text_extractor.extract_text_from_html(self.html_content)

        self.assertEqual(expected, extracted_text)
