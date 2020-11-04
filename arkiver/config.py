import os
import sys
import json
import logging

from xdg import xdg_config_home

log = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"

ENV_VERBOSE = "ARKIVER_VERBOSE"
ENV_CONFIG = "ARKIVER_CONFIG"
ENV_ARCHIVE = "ARKIVER_ARCHIVE"


def _get_config_file():
    return (
        os.environ.get(ENV_CONFIG)
        or os.path.join(xdg_config_home(), "arkiver/arkiver.conf")
        or os.path.expanduser("~/.arkiver")
    )


def _from_file(config_file):
    if os.path.isfile(os.path.expanduser(config_file)):
        with open(config_file, "r") as f:
            return json.load(f)


def _from_environment():
    cfg = {
        "verbose": bool(os.environ.get(ENV_VERBOSE)),
        "archive": os.environ.get(ENV_ARCHIVE),
    }

    return {k: v for k, v in cfg.items() if v is not None}


def load():
    config_file = _get_config_file()
    log.debug(config_file)

    config = {}
    config.update(_from_file(config_file))
    config.update(_from_environment())

    return config
