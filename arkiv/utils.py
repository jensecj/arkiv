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
