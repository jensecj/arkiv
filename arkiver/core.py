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


# TODO: wrap each section in an error handler
def archive(config, url):
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
