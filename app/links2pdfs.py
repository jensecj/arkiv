import os
import sys
import subprocess
from urllib.parse import urlparse, urljoin

from shell_utils import shell


def _download_pdf(url):
    print(f"downloading pdf: {url}")
    base = urlparse(url)
    basename = os.path.basename(base.path)
    filename = os.path.join("pdfs", basename)

    if not filename.endswith(".pdf"):
        filename = filename + ".pdf"

    args = [
        "-e",
        "robots=off",
        "--no-verbose",
        "--progress=bar",
        "--show-progress",
        "--wait=1",
        "--random-wait",
        "--user-agent=Mozilla",
        "-O",
        filename,
    ]

    cmd = ["wget"] + args + [url]

    return_code, stdout, stderr = shell(cmd)

    if return_code:
        print(
            f"failed to download, skipping. return_code: {return_code}. stderr: {stderr}"
        )


def _get_pdf_links(links):
    return [l for l in links if l.endswith(".pdf")]


def _get_direct_arxiv_links(links):
    return [l for l in links if "arxiv.org/pdf/" in l]


def _get_indirect_arxiv_links(links):
    indirect_arxiv = [l for l in links if "arxiv.org/abs/" in l]
    clean_indirect_arxiv = set()

    for l in indirect_arxiv:
        base = urlparse(l)
        lnk = base.scheme + "://" + base.netloc + base.path
        lnk = lnk.replace("arxiv.org/abs/", "arxiv.org/pdf/")
        clean_indirect_arxiv.add(lnk)

    return clean_indirect_arxiv


def _dedupe_links(links):
    # cleanup duplicated arxiv pdf links, arxiv-versions, etc
    pdfs = set()
    for s in sorted(links, reverse=True):
        if not any([s in o for o in pdfs]):
            pdfs.add(s)

    return pdfs


def extract_pdfs(config, links):
    print("downloading pdf files...")

    try:

        all_links = links["internal"] + links["external"]
        all_links = [l for l in all_links if not "ignore_me" in l]

        pdf_links = set()

        pdf_links.update(_get_pdf_links(all_links))
        pdf_links.update(_get_direct_arxiv_links(all_links))

        if config.get("indirect_arxiv"):
            pdf_links.update(_get_indirect_arxiv_links(all_links))

        if len(pdf_links) > 0:
            if not os.path.isdir("pdfs"):
                os.mkdir("pdfs")

        for l in _dedupe_links(pdf_links):
            _download_pdf(l)
    except KeyboardInterrupt:
        print("user interrupted handler, skipping...")
    except Exception as error:
        print(repr(error))
