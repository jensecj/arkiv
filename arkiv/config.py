import os
import sys
import json
import logging

from xdg import xdg_config_home

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(message)s"},
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
    },
    "handlers": {
        "default": {
            "formatter": "simple",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "extended": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "urllib3.connectionpool": {"level": "WARNING", "propagate": False},
        "selenium.webdriver.remote.remote_connection": {
            "level": "WARNING",
            "propagate": False,
        },
        "readability": {"level": "WARNING", "propagate": False},
    },
    "root": {
        "handlers": ["default"],
        "level": "INFO",
        "propagate": False,
    },
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"

ENV_CONFIG = "ARKIV_CONFIG"
ENV_ARCHIVE = "ARKIV_ARCHIVE"


log = logging.getLogger(__name__)


def _get_config_file():
    # paths to config file, in the ordere they're checked
    paths = [
        os.environ.get(ENV_CONFIG),
        os.path.join(xdg_config_home(), "arkiv/arkiv.conf"),
        os.path.expanduser("~/.arkiv/arkiv.conf"),
        os.path.expanduser("~/.arkiv"),
    ]

    for p in paths:
        if p and os.path.isfile(p):
            return p  # use the first valid config file


def _from_file(config_file):
    with open(os.path.expanduser(config_file), "r") as f:
        return json.load(f)


def _from_environment():
    cfg = {
        "archive": os.environ.get(ENV_ARCHIVE),
    }

    # only return keys with valid values
    return {k: v for k, v in cfg.items() if v is not None}


def load():
    config_file = _get_config_file()
    log.debug(f"{config_file=}")

    config = {}
    config.update(_from_file(config_file))
    config.update(_from_environment())
    log.debug(f"{config=}")

    return config
