import sys
import subprocess
import logging

from ..utils import shell, wget, profile


log = logging.getLogger(__name__)


@profile
def generate(url):
    log.info("generating WARC...")

    extra_args = [
        "--warc-file=archive",
        "--convert-links",
        "--span-hosts",
        "--adjust-extension",
        "--level=1",
        "--page-requisites",
        "--delete-after",
        # "--waitretry=600",
        # "--span-hosts-allow=linked-pages,page-requisites",
        # "--escaped-fragment",
        # "--strip-session-id",
        # "--retry-connrefused",
        # "--retry-dns-error",
        # "--session-timeout=21600",
    ]

    # TODO: exclude domains

    wget(url, extra_args=extra_args)
