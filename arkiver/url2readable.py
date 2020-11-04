import requests
from readability import Document
from html2text import HTML2Text
import re
import logging

from config import USER_AGENT

log = logging.getLogger(__name__)


def generate_readable(url):
    log.info("generating readable file...")

    headers = requests.utils.default_headers()
    headers.update({"User-Agent": USER_AGENT})

    response = requests.get(url, headers=headers)
    doc = Document(response.text)
    html = doc.summary()

    parser = HTML2Text()
    parser.wrap_links = False
    parser.inline_links = True
    text = parser.handle(html)
    text = text.replace("\\n", "")
    text = re.sub(r"\n\s*\n", "\n\n", text)
    text = text.strip()

    with open("readable.txt", "w") as f:
        f.write(text)
