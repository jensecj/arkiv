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

logging.config.dictConfig(CFG.LOG_CONFIG)

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
@click.option("-v", "--verbose", help="", is_flag=True)
@click.option("-V", "--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True,)
def main(url, verbose):
    if verbose:
        os.environ[CFG.ENV_VERBOSE] = "true"

    log.info("archiving " + url)

    config = CFG.load()

    link = urlparse(url)
    loc = link.netloc.strip("/")
    path = link.path.strip("/")

    # maybe store timestamped dirs in this path, instead of prefixing with date?
    archive_path = f"{loc}--{path}"
    if q := link.query:
        archive_path = archive_path + "?" + q

    archive_path = (
        archive_path.replace("www.", "")
        .replace(".html", "")
        .replace(".htm", "")
        .replace(".asp", "")
        .replace(".aspx", "")
        .replace(".php", "")
        .replace("/", "_")
    )

    archive_path = archive_path[:75]
    log.debug(f"{archive_path=}")

    if p := config.get("archive"):
        path = os.path.join(os.path.expanduser(p), archive_path)
    else:
        path = os.path.abspath(archive_path)

    if not os.path.isdir(path):
        os.mkdir(path)

    os.chdir(path)

    archive(config, url)


if __name__ == "__main__":
    main()
