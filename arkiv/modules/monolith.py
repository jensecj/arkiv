import logging
import shutil

from ..utils import shell


log = logging.getLogger(__name__)


def generate(url):
    log.info("generating monolith...")
    if not shutil.which("monolith"):
        log.error("could not find `monolith' executable, skipping.")
        return

    args = ["-s", "-o", "monolith.html"]
    cmd = ["monolith"] + args + [url]

    return_code, stdout, stderr = shell(cmd)

    if return_code:
        log.debug(f"{stdout=}")
        log.debug(f"{stderr=}")
        log.debug(f"{return_code=}")
        log.error(f"failed to generate monolith, skipping.")
