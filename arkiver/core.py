import logging

from url2meta import gather_meta
from url2links import gather_links
from url2readable import generate_readable
from url2singlefile import generate_singlefile
from url2img import generate_screenshots
from url2pdf import generate_pdfs
from url2archive import generate_archive
from url2warc import generate_warc

from links2repos import extract_repos
from links2videos import extract_videos
from links2images import extract_images
from links2pdfs import extract_pdfs


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
