import json
import logging

from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urlparse, urljoin

from config import USER_AGENT

log = logging.getLogger(__name__)


def gather_links(url):
    log.info("gathering links...")

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    resp = urllib.request.urlopen(req)
    soup = BeautifulSoup(
        resp, from_encoding=resp.info().get_param("charset"), features="html.parser"
    )

    links = []
    for link in soup.find_all("a", href=True):
        links.append(urljoin(url, link.get("href")))

    base = urlparse(url).netloc

    internal = [l for l in links if base in l]
    external = [l for l in links if base not in l]

    with open("links.json", "w") as f:
        json.dump({"internal": internal, "external": external}, f, indent=4)
