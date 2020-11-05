import subprocess
import logging

log = logging.getLogger(__name__)


def shell(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)

    return_code = popen.wait()
    stdout = popen.stdout.read()
    stderr = popen.stderr.read() if popen.stderr else None

    return return_code, stdout, stderr
