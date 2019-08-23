import os
import sys
import subprocess
import shutil

from config import USER_AGENT


def _shell_cmd(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for output in iter(popen.stdout.readline, ""):
        print(output)

    popen.stdout.close()
    return_code = popen.wait()

    return return_code


def _download_archive(url):
    print("downloading website...")

    args = [
        "--convert-links",
        "--span-hosts",
        "--adjust-extension",
        "-e",
        "robots=off",
        "--show-progress",
        "--page-requisites",
        "--no-verbose",
        "--directory-prefix=archive",
        "--level=1",
        "--wait=1",
        "--random-wait",
        "--user-agent=Mozilla",
    ]

    cmd = ["wget"] + args + [url]

    return_code = _shell_cmd(cmd)

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
            f"Failed to download website. return code: {return_code} ({err}). stderr: {popen.stderr}"
        )

    if return_code == 5:
        print("failed to validate SSL, trying to continue anyway...")


def _compress_archive(path):
    print("compressing into archive...")

    args = ["-czf"]
    cmd = ["tar"] + args + ["archive.tar.gz", path]

    return_code = _shell_cmd(cmd)

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
            print(
                "error removing website directory: %s - %s." % (e.filename, e.strerror)
            )


def generate_archive(url):
    print("generating website archive...")

    print("=====")

    try:
        _download_archive(url)

        path = os.path.join(os.path.curdir, "archive/")
        _compress_archive(path)
    except Exception as error:
        err = repr(error)
        print(f"ERROR: {err}")

    print("=====")
