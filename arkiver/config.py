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
        "debug": {
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
        "handlers": ["debug"],
        "level": "DEBUG",
        "propagate": False,
    },
}


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"

ENV_VERBOSE = "ARKIVER_VERBOSE"
ENV_CONFIG = "ARKIVER_CONFIG"
ENV_ARCHIVE = "ARKIVER_ARCHIVE"


log = logging.getLogger(__name__)


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
