import sys
import os
import asyncio
import logging
from urllib.parse import urlparse, urljoin
import datetime
import json

from url2meta import gather_meta
from url2links import gather_links
from url2readable import generate_readable
from url2singlefile import generate_singlefile
from url2img import generate_images
from url2pdf import generate_pdfs
from url2archive import generate_archive
from url2warc import generate_warc

from links2pdfs import extract_pdfs


# TODO: wrap each section in an error handler
async def process(config, url):
    gather_meta(url)
    gather_links(url)
    generate_readable(url)
    generate_singlefile(url)

    await generate_images(url)
    await generate_pdfs(url)

    links_file = os.path.abspath("links.json")
    links = []

    if os.path.isfile(links_file):
        with open(links_file, "r") as f:
            links = json.load(f)

    if links:
        extract_pdfs(config, links)
    generate_warc(config, url)
    generate_archive(config, url)

    print("Archiving complete.")


def read_config():
    config_file = os.environ.get("ARKIVER_CONFIG") or os.path.expanduser("~/.arkiver")
    if os.path.isfile(config_file):
        with open(config_file, "r") as f:
            return json.load(f)


def main():
    if len(sys.argv) < 2:
        print("usage: arkiver <url>")
        sys.exit()

    url = sys.argv[1]
    print("archiving " + url)

    config = read_config()

    if config.get("timestamp-output"):
        logging.basicConfig(
            format="%(asctime)s %(message)s:", datefmt="%Y-%d-%m %H:%M:%S"
        )

    date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M")

    link = urlparse(url)

    # maybe store timestamped dirs in this path, instead of prefixing with date?
    archive_path = date + "--" + link.netloc + link.path
    if link.query:
        archive_path = archive_path + "?" + link.query

    archive_path = (
        archive_path.replace(".html", "")
        .replace(".htm", "")
        .replace(".asp", "")
        .replace(".aspx", "")
        .replace("/", "_")[:75]
    )

    if p := config.get("path"):
        path = os.path.join(os.path.expanduser(p), archive_path)
    else:
        path = os.path.abspath(archive_path)

    if not os.path.isdir(path):
        os.mkdir(path)

    os.chdir(path)

    asyncio.get_event_loop().run_until_complete(process(config, url))


if __name__ == "__main__":
    main()
