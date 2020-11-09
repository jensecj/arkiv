import os
import logging
from urllib.parse import urlparse

from ..utils import shell, wget

log = logging.getLogger(__name__)


def _download_pdf(url):
    log.info(f"downloading arxiv: {url}")

    base = urlparse(url)
    basename = os.path.basename(base.path)
    filename = os.path.join("arxiv", basename)

    if not filename.endswith(".pdf"):
        filename = filename + ".pdf"

    wget(url, filename)


def extract(links):
    all_links = links["internal"] + links["external"]

    direct = [l for l in all_links if "arxiv.org/pdf/" in l]
    indirect = [l for l in all_links if "arxiv.org/abs/" in l]

    indirect = [l.replace("arxiv.org/abs/", "arxiv.org/pdf/") for l in indirect]

    pdf_links = set()
    pdf_links.update(direct)
    pdf_links.update(indirect)

    if len(pdf_links) > 0:
        if not os.path.isdir("arxiv"):
            os.mkdir("arxiv")

    for l in sorted(pdf_links):
        _download_pdf(l)
