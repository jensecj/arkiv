import sys
import os
import asyncio
import logging

logging.basicConfig(format="%(asctime)s %(message)s:", datefmt="%Y-%d-%m %H:%M:%S")

from url2meta import gather_meta
from url2links import gather_links
from url2img import generate_images
from url2pdf import generate_pdfs
from url2warc import generate_warc


async def process(url):
    gather_meta(url)
    gather_links(url)
    await generate_images(url)
    await generate_pdfs(url)
    generate_warc(url)

    print("Archiving complete.")


def main():
    if len(sys.argv) < 2:
        print("usage: warc-hive <url>")
        sys.exit()

    url = sys.argv[1]
    print("archiving " + url)
    asyncio.get_event_loop().run_until_complete(process(url))


if __name__ == "__main__":
    main()
