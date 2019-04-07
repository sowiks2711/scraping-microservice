from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup


def _is_correct_response(resp) -> bool:
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e) -> None:
    print(e)


class WebsiteScraper:
    def __init__(self):
        pass

    def scrap(self, url):
        pass


class HtmlResourceProvider:
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
        soup = BeautifulSoup(html_content)

        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text()

        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
