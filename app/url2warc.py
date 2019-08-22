import sys
import subprocess

from config import USER_AGENT


def generate_warc(url):
    print("generating WARC archive...")

    args = [
        url,
        "--warc-file",
        "site",
        "--no-check-certificate",
        "--no-robots",
        "--wait",
        "0.5",
        "--random-wait",
        "--waitretry",
        "600",
        "--page-requisites",
        "--span-hosts-allow",
        "linked-pages,page-requisites",
        "--escaped-fragment",
        "--strip-session-id",
        "--tries",
        "3",
        "--retry-connrefused",
        "--retry-dns-error",
        "--timeout",
        "60",
        "--session-timeout",
        "21600",
        "--delete-after",
        "--user-agent",
        USER_AGENT,
        "--concurrent",
        "2",
    ]

    cmd = ["wpull"] + args

    print("=====")

    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for output in iter(popen.stdout.readline, ""):
        print(output)
    popen.stdout.close()

    return_code = popen.wait()

    if return_code:
        print("Error generating WARC archive!")
        print(popen.stderr)
        sys.exit()

    print("=====")
