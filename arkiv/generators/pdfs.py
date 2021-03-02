import os
import logging
from urllib.parse import urlparse

from ..utils import shell, wget, profile

log = logging.getLogger(__name__)


def _download_pdf(url):
    log.info(f"- downloading {url}")
    base = urlparse(url)
    basename = os.path.basename(base.path)
    filename = os.path.join("pdfs", basename)

    if not filename.endswith(".pdf"):
        filename = filename + ".pdf"

    wget(url, dest_file=filename, extra_args=["--show-progress"])


@profile
def generate(links):
    log.info("generating pdf files...")

    all_links = links["internal"] + links["external"]
    pdf_links = set([l for l in all_links if l.endswith(".pdf")])

    if len(pdf_links) > 0:
        if not os.path.isdir("pdfs"):
            os.mkdir("pdfs")

    for l in sorted(pdf_links):
        _download_pdf(l)
