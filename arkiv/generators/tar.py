import os
import sys
import subprocess
import shutil
import logging

from ..utils import shell, wget, tar, time

log = logging.getLogger(__name__)

TMP_ARCHIVE = "tar_archive_tmp/"


@time
def _download_mirror(url, dest):
    log.info("- downloading website mirror...")

    extra_args = [
        "--convert-links",
        "--span-hosts",
        "--adjust-extension",
        "--page-requisites",
        "--level=1",
    ]

    # TODO: exclude domains

    wget(url, dest_dir=dest, extra_args=extra_args)


def _compress_archive(files, dest):
    log.info("- compressing into archive...")
    tar(files, dest)


def generate(url):
    log.info("generating tar archive...")

    mirror_path = os.path.join(os.path.curdir, TMP_ARCHIVE)
    log.debug(f"{mirror_path=}")

    _download_mirror(url, mirror_path)
    _compress_archive([mirror_path], "archive.tar.gz")

    try:
        shutil.rmtree(mirror_path)
    except OSError as e:
        log.error(f"failed to remove temporary archive dir")
        log.debug(f"{e.stderror=}")
