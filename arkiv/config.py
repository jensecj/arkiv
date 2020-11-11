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
        "standard": {
            "format": "%(asctime)s [%(levelname)-7s] %(name)s:%(lineno)s: %(message)s"
        },
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(asctime)s %(log_color)s[%(levelname)-7s]%(reset)s %(white)s%(name)s:%(lineno)s%(reset)s: %(message)s",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
            },
        },
    },
    "handlers": {
        "default": {
            "formatter": "simple",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "extended": {
            "formatter": "colored",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "git.cmd": {"level": "WARNING", "propagate": False},
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

CONFIG = {}

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

    return os.path.join(xdg_config_home(), "arkiv/arkiv.conf")


def _from_file(config_file):
    with open(os.path.expanduser(config_file), "r") as f:
        return json.load(f)

    return {}


def _from_environment():
    cfg = {
        "archive": os.environ.get(ENV_ARCHIVE),
    }

    # only return keys with valid values
    return {k: v for k, v in cfg.items() if v is not None}


def load():
    config_file = _get_config_file()
    log.debug(f"{config_file=}")

    file_config = _from_file(config_file)
    log.debug(f"{file_config=}")

    env_config = _from_environment()
    log.debug(f"{env_config=}")

    config = {}
    config.update(file_config)
    config.update(env_config)
    log.debug(f"{config=}")

    return config
