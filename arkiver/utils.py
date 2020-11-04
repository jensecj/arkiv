import subprocess
import logging

log = logging.getLogger(__name__)


def shell(cmd, input=None, log=True):
    popen = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True
    )

    if input:
        if not isinstance(input, list):
            input = [input]

        for i in input:
            popen.stdin.write(i)
            popen.stdin.flush()

        popen.stdin.close()

    output = ""
    if log:
        for o in iter(popen.stdout.readline, ""):
            output.append(o)
            log.info(o)
    else:
        output = popen.stdout.read()

    return_code = popen.wait()

    err = popen.stderr.read() if popen.stderr else None

    return return_code, output, err
