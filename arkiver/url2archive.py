import os
import sys
import subprocess
import shutil
import logging

from config import USER_AGENT
from shell_utils import shell

log = logging.getLogger(__name__)


def _download_archive(config, url):
    log.info("downloading website...")

    args = [
        "--convert-links",
        "--span-hosts",
        "--adjust-extension",
        "-e",
        "robots=off",
        "--progress=bar",
        "--show-progress",
        "--page-requisites",
        "--no-verbose",
        "--directory-prefix=archive",
        "--level=1",
        "--wait=1",
        "--random-wait",
        "--user-agent=Mozilla",
    ]

    extra_args = []
    if config.get("exclude_domains"):
        domains = ",".join(config["exclude_domains"])
        extra_args = extra_args + ["--exclude-domains", domains]

    cmd = ["wget"] + args + extra_args + [url]

    return_code, stdout, stderr = shell(cmd)

    if return_code and return_code != 5:
        errors = [
            "no error",
            "generic error",
            "parse error",
            "I/O error",
            "network failure",
            "SSL failure",
            "auth failure",
            "protocol error",
            "server error response",
        ]

        err = errors[return_code]

        raise Exception(
            f"Failed to download website. return code: {return_code} ({err}). stderr: {stderr}"
        )

    if return_code == 5:
        log.warning("failed to validate SSL, trying to continue anyway...")


def _compress_archive(path):
    log.info("compressing into archive...")

    args = ["-czf"]
    cmd = ["tar"] + args + ["archive.tar.gz", path]

    return_code, stdout, stderr = shell(cmd)

    if return_code:
        errors = ["no error", "some files changed", "fatal error"]
        err = errors[return_code]
        raise RuntimeError(
            f"Failed to compress website into archive. return code: {return_code} ({err}). stderr: {popen.stderr}"
        )
    else:
        try:
            shutil.rmtree(path)
        except OSError as e:
            log.error(
                "error removing website directory: %s - %s." % (e.filename, e.strerror)
            )


def generate_archive(config, url):
    log.info("generating website archive...")

    try:
        _download_archive(config, url)

        path = os.path.join(os.path.curdir, "archive/")
        _compress_archive(path)
    except KeyboardInterrupt:
        log.info("user interrupted handler, skipping...")
    except Exception as error:
        log.error(repr(error))
