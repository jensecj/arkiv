import shutil
import time
import subprocess
import logging

from .config import USER_AGENT

log = logging.getLogger(__name__)


def profile(fn):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter_ns()
        ret = fn(*args, **kwargs)
        end_time = time.perf_counter_ns()

        elapsed = end_time - start_time

        micro, nano = divmod(elapsed, 1000)
        milli, micro = divmod(micro, 1000)
        seconds, milli = divmod(milli, 1000)

        log.debug(
            f"`{fn.__module__}.{fn.__qualname__}' took {seconds}s {milli}ms {micro}μs {nano}ns"
        )
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
        "--timeout=10",
        "--user-agent=" + f"'{USER_AGENT}'",
        "--no-check-certificate",
        "--no-parent",
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

    return return_code == 0
