import os
import time
import uuid

from requests import get, Response
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

from definitions import IMAGES_DIR, ARCHIVES_DIR
import shutil


def _is_correct_response(resp: Response) -> bool:
    content_type: str = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e: RequestException) -> None:
    print(e)


class HtmlContentProvider:
    def get_html(self, url: str) -> str:
        try:
            with closing(get(url, stream=True)) as resp:
                if _is_correct_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            log_error('Error during requests to {0} : {1}'.format(url, str(e)))
            return None


class TextExtractor:
    def extract_text_from_html(self, html_content: str) -> str:
        soup = BeautifulSoup(html_content, "html.parser")

        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text()

        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text


class ImageScraper:
    def __init__(self, url: str, html_content_extractor: HtmlContentProvider = HtmlContentProvider()):
        self._html_content_extractor = html_content_extractor
        self.url = url
        self._images_folder_name = self.url_to_folder_name(url) + str(uuid.uuid4())
        self._images_folder_path = os.path.join(IMAGES_DIR, self._images_folder_name)

    def url_to_folder_name(self, url: str) -> str:
        txt: str = ''.join(url.split('/'))
        colon_index: int = txt.find(':')
        if colon_index != -1:
            txt = txt[colon_index+1:]

        return txt

    def pull_images_from_html_references(self) -> None:
        html_content: str = self._html_content_extractor.get_html(self.url)
        soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
        self.create_image_dir()

        for res in soup.findAll('img'):
            print(res.get('src'))
            src: str = res.get('src')
            if src is not None and 'data' in str(src):
                continue
            src: str = src if src is not None else res.get('data-src')

            self._save_image(src)
            while True:
                if os.path.isdir(self._images_folder_path):
                    break
                time.sleep(5)
        archive_path = os.path.join(ARCHIVES_DIR, self._images_folder_name)
        shutil.make_archive(archive_path, 'zip', self._images_folder_path)

    def _save_image(self, src):
        with closing(get(src, stream=True)) as resource:
            if resource.status_code == 200:
                filepath = os.path.join(self._images_folder_path, src.split('/')[-1])
                with open(filepath, 'wb') as f:
                    for chunk in resource:
                        f.write(chunk)

    def create_image_dir(self):
        os.mkdir(self._images_folder_path)


class WebsiteScraper:
    def __init__(self, html_content_provider: HtmlContentProvider, text_extractor: TextExtractor):
        self._html_content_provider: HtmlContentProvider = html_content_provider
        self._text_extractor: TextExtractor = text_extractor

    def scrap_text(self, url: str) -> str:
        html_content: str = self._html_content_provider.get_html(url)
        return self._text_extractor.extract_text_from_html(html_content)

