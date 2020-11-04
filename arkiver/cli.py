import sys
import os
import logging, logging.config
from urllib.parse import urlparse, urljoin
import json

import click

from url2meta import gather_meta
from url2links import gather_links
from url2readable import generate_readable
from url2singlefile import generate_singlefile
from url2img import generate_screenshots
from url2pdf import generate_pdfs
from url2archive import generate_archive
from url2warc import generate_warc

from links2pdfs import extract_pdfs

import config as CFG


log = logging.getLogger(__name__)


# TODO: wrap each section in an error handler
def archive(config, url):
    meta = gather_meta(url)
    links = gather_links(url)
    # generate_readable(url)
    # generate_singlefile(url)
    generate_screenshots(url)
    # await generate_pdfs(url)

    if links:
        extract_pdfs(config, links)

    generate_warc(config, url)
    generate_archive(config, url)

    log.info("Archiving complete")


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    version = open("__version__.py", "r").read().strip()
    log.info(f"arkiver v{version}")
    ctx.exit()


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("url", type=str)
@click.option("-v", "--verbose", help="", count=True)
@click.option("-V", "--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True,)
def main(url, verbose):
    verbosity = {
        0: {"root": {"handlers": ["default"], "level": "INFO"}},
        1: {"root": {"handlers": ["extended"], "level": "INFO"}},
        2: {"root": {"handlers": ["extended"], "level": "DEBUG"}},
    }
    CFG.LOG_CONFIG.update(verbosity.get(verbose))
    logging.config.dictConfig(CFG.LOG_CONFIG)

    config = CFG.load()

    log.info(f"archiving {url}")

    link = urlparse(url)
    loc = link.netloc.strip("/")
    path = link.path.strip("/")

    archive_dir = f"{loc}--{path}"

    # replace common parts of the path
    archive_dir = (
        archive_dir.replace("www.", "")
        .replace(".html", "")
        .replace(".htm", "")
        .replace(".asp", "")
        .replace(".aspx", "")
        .replace(".php", "")
        .replace("/", "_")
    )

    # append fragment and query parts of the path
    if fragment := link.fragment:
        archive_dir = archive_dir + "#" + fragment
    if query := link.query:
        archive_dir = archive_dir + "?" + query

    # cap the length of the archives name
    archive_dir = archive_dir[:75]

    log.debug(f"{archive_dir=}")

    if p := config.get("archive"):
        archive_path = os.path.join(os.path.expanduser(p), archive_dir)
    else:
        archive_path = os.path.abspath(archive_dir)

    if not os.path.isdir(archive_path):
        os.mkdir(archive_path)

    os.chdir(archive_path)

    archive(config, url)


if __name__ == "__main__":
    main()
