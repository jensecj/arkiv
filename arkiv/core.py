import os
from urllib.parse import urlparse
import logging

from .modules.url2meta import gather_meta
from .modules.url2links import gather_links
from .modules.url2readable import generate_readable
from .modules.url2singlefile import generate_singlefile
from .modules.url2img import generate_screenshots
from .modules.url2pdf import generate_pdfs
from .modules.url2archive import generate_archive
from .modules.url2warc import generate_warc

from .modules.links2repos import extract_repos
from .modules.links2videos import extract_videos
from .modules.links2images import extract_images
from .modules.links2pdfs import extract_pdfs


log = logging.getLogger(__name__)


def _build_archive_dir(url):
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

    return archive_dir


def archive(config, url):
    log.info(f"archiving {url}")

    archive_dir = _build_archive_dir(url)
    if p := config.get("archive"):
        archive_path = os.path.join(os.path.expanduser(p), archive_dir)
    else:
        archive_path = os.path.abspath(archive_dir)

    log.debug(f"{archive_path=}")

    if not os.path.isdir(archive_path):
        os.mkdir(archive_path)

    os.chdir(archive_path)

    # TODO: wrap each section in an error handler
    meta = gather_meta(url)
    links = gather_links(url)
    generate_readable(url)
    generate_screenshots(url)
    # generate_singlefile(url)
    # await generate_pdfs(url)

    if links:
        extract_pdfs(config, links)
        extract_images(links)
        extract_videos(links)
        extract_repos(links)

    # generate_warc(config, url)
    # generate_archive(config, url)

    log.info("Archiving complete")
