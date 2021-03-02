import logging
import tempfile
import tarfile
import shutil

from ..utils import shell, wget, profile

log = logging.getLogger(__name__)


def _download_mirror(url, dest):
    log.info("downloading website mirror...")

    extra_args = [
        "--convert-links",
        # "--span-hosts",
        "--adjust-extension",
        # "--page-requisites",
        "--level=1",
    ]

    # TODO: exclude domains
    return wget(url, dest_dir=dest, extra_args=extra_args)


def _compress_archive(files, dest):
    log.info("compressing into archive...")
    try:
        with tempfile.NamedTemporaryFile(suffix=".tar.gz") as tmp:
            with tarfile.open(fileobj=tmp, mode="w:gz") as f:
                f.add(files, arcname=".")

            shutil.copy(tmp.name, "archive.tar.gz")
    except Exception as ex:
        log.error(f"[red]failed to compress archive: {ex}")


@profile
def generate(url):
    log.info("generating tar archive...")

    with tempfile.TemporaryDirectory() as mirror_path:
        if _download_mirror(url, mirror_path):
            _compress_archive(mirror_path, "archive.tar.gz")
        else:
            log.error("[red]failed to download mirror")
