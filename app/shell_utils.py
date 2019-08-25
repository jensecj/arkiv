import subprocess


def shell_cmd(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for output in iter(popen.stdout.readline, ""):
        print(output)

    popen.stdout.close()
    return_code = popen.wait()

    return return_code, popen.stderr
