import sys
import subprocess

from config import USER_AGENT
from shell_utils import shell_cmd


def _generate(config, url):
    args = [
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

    extra_args = []
    if config.get("exclude_domains"):
        domains = ",".join(config["exclude_domains"])
        extra_args = extra_args + ["--exclude-domains", domains]
        extra_args = extra_args + ["--exclude-hostnames", domains]

    cmd = ["wpull"] + args + extra_args + [url]

    return_code, stderr = shell_cmd(cmd)

    if return_code:
        raise Exception(
            f"failed to generate WARC. return code: {return_code}. stderr: {stderr}"
        )


def generate_warc(config, url):
    print("generating WARC archive...")

    print("=====")

    try:
        _generate(config, url)
    except KeyboardInterrupt:
        print("user interrupted handler, skipping...")
    except Exception as error:
        print(repr(error))

    print("=====")
