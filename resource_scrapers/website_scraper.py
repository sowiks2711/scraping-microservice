import os
import time
import uuid

from requests import get, Response
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

from definitions import IMAGES_DIR, ARCHIVES_DIR, TEXTS_DIR
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


def url_to_folder_name(url: str) -> str:
    txt: str = ''.join(url.split('/'))
    colon_index: int = txt.find(':')
    if colon_index != -1:
        txt = txt[colon_index+1:]

    return txt


def save_data_in_file(dir_path, filename, resource, mode='binary'):
    filepath = os.path.join(dir_path, filename)
    if mode == 'binary':
        mode = 'wb'
    elif mode == 'text':
        mode ='w'
    else:
        raise ValueError(f'Only "binary" and "text" mode are allowed. Mode {mode} is not supported')
    with open(filepath, mode) as f:
        for chunk in resource:
            f.write(chunk)


class ImageScraper:
    def __init__(self, url: str, task_id: str, html_content_extractor: HtmlContentProvider = HtmlContentProvider()):
        self._html_content_extractor: HtmlContentProvider = html_content_extractor
        self.url: str = url
        self.resource_guid: str = task_id
        self.images_folder_name: str = '_'.join([url_to_folder_name(url), self.resource_guid])
        self._images_folder_path: str = os.path.join(IMAGES_DIR, self.images_folder_name)

    def pull_images_from_html_references(self) -> None:
        html_content: str = self._html_content_extractor.get_html(self.url)
        soup: BeautifulSoup = BeautifulSoup(html_content, "html.parser")
        self.create_image_dir()

        for res in soup.findAll('img'):
            print(res.get('src'))
            src: str = res.get('src')


            src: str = src if src is not None else res.get('data-src')

            if src is None or src == '' or src[0] == '/' or 'data' in src:
                continue

            if src is not None:
                src = f'https:{src}' if src[:2] == '//' else src

            self._save_image(src)
            while True:
                if os.path.isdir(self._images_folder_path):
                    break
                time.sleep(5)
        archive_path = os.path.join(ARCHIVES_DIR, self.images_folder_name)
        shutil.make_archive(archive_path, 'zip', self._images_folder_path)

    def _save_image(self, src):
        with closing(get(src, stream=True)) as resource:
            filename: str = src.split('/')[-1]
            dir_path: str = self._images_folder_path
            if resource.status_code == 200:
                save_data_in_file(dir_path, filename, resource)

    def create_image_dir(self):
        os.mkdir(self._images_folder_path)


class TextScraper:

    def __init__(self, url: str, task_id: str, html_content_extractor: HtmlContentProvider = HtmlContentProvider(),
                 text_extractor: TextExtractor = TextExtractor()):
        self._html_content_extractor: HtmlContentProvider = html_content_extractor
        self._text_extractor = text_extractor
        self.url: str = url
        self.resource_guid: str = task_id
        self.texts_file_name: str = '_'.join([url_to_folder_name(self.url), self.resource_guid])

    def pull_texts(self):
        html_content: str = self._html_content_extractor.get_html(self.url)
        text = self._text_extractor.extract_text_from_html(html_content)
        save_data_in_file(TEXTS_DIR, '.'.join([self.texts_file_name, 'txt']), text, 'text')




