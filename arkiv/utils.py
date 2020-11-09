import shutil
from datetime import datetime
import subprocess
import logging


log = logging.getLogger(__name__)


def time(fn):
    def wrapper(*args, **kwargs):
        start_time = datetime.now()

        ret = fn(*args, **kwargs)

        end_time = datetime.now()
        elapsed = end_time - start_time
        log.debug(f"fn `{fn.__name__}' completed in {elapsed}")

        return ret

    return wrapper


def shell(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)

    return_code = popen.wait()
    stdout = popen.stdout.read()
    stderr = popen.stderr.read() if popen.stderr else None

    return return_code, stdout, stderr


def wget(url, dest_file=None, dest_dir=None, extra_args=[]):
    if not shutil.which("wget"):
        log.error("could not find `wget' executable, skipping.")
        return

    args = [
        "--execute",
        "robots=off",
        "--no-verbose",
        "--quiet",
        "--progress=bar",
        "--wait=1",
        "--random-wait",
        "--tries=5",
        "--user-agent=Mozilla",
        "--no-check-certificate",
    ]

    if dest_file:
        args += ["-O", dest_file]

    if dest_dir:
        args += [f"--directory-prefix={dest_dir}"]

    cmd = ["wget"] + args + extra_args + [url]
    return_code, stdout, stderr = shell(cmd)

    errors = ["no error", "some files changed", "fatal error"]

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

    if return_code:
        log.error(f"failed to download {url}: {err}")
        log.debug(f"{return_code=}")
        log.debug(f"{stdout=}")
        log.debug(f"{stderr=}")


def tar(files, dest, extra_args=[]):
    args = ["-czf"]
    cmd = ["tar"] + args + extra_args + [dest] + files

    return_code, stdout, stderr = shell(cmd)

    errors = ["no error", "some files changed", "fatal error"]
    err = errors[return_code]

    if return_code:
        log.error(f"Failed to compress website into archive: {err}")
        log.debug(f"{return_code=}")
        log.debug(f"{stdout=}")
        log.debug(f"{stderr=}")
