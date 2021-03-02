import os
import json
import time
import logging
from logging import Handler, LogRecord

import rich
from rich.console import Console
from rich.table import Table
from rich.text import Text
from xdg import xdg_config_home


log_console = Console(highlight=False, emoji=False)


class LogHandler(Handler):
    def __init__(
        self,
        console=None,
        level=logging.NOTSET,
        show_time: bool = False,
        show_level: bool = False,
        show_path: bool = False,
        log_colors: dict[str, str] = None,
        log_level_colors: dict[str, str] = None,
    ) -> None:
        super().__init__(level=level)
        self.console = console or rich.get_console()
        self.formatter = self.formatter or logging._defaultFormatter
        self.show_time = show_time
        self.show_level = show_level
        self.show_path = show_path
        self.log_colors = log_colors or {
            "time": "blue",
            "path": "dim white",
        }
        self.log_level_colors = log_level_colors or {
            "INFO": "bold white",
            "WARNING": "yellow",
            "DEBUG": "cyan",
            "ERROR": "red",
        }

    def emit(self, record: LogRecord) -> None:
        output = Table.grid(padding=(0, 1))
        output.expand = True
        output.add_column()
        output.add_column()
        output.add_column()
        output.add_column(ratio=1, overflow="fold")

        row = []

        log_time = ""
        if self.show_time:
            log_time = f"{self.formatter.formatTime(record)}"
            color = self.log_colors.get("time")
            row.append(Text(log_time, style=color))

        log_level = ""
        if self.show_level:
            log_level = f"{record.levelname:<7}"
            color = self.log_level_colors.get(record.levelname)
            row.append(Text(log_level, style=color))

        log_path = ""
        if self.show_path:
            log_path = f"{record.name}:{record.lineno}"
            color = self.log_colors.get("path")
            row.append(Text(log_path, style=color))

        log_message = record.getMessage()
        row.append(log_message)

        output.add_row(*row)
        # items = [*filter(None, [log_time, log_level, log_path, log_message])]
        # self.console.print(*items)
        self.console.print(output)


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "default": {
            "class": "arkiv.config.LogHandler",
            "console": log_console,
        },
        "extended": {
            "class": "arkiv.config.LogHandler",
            "console": log_console,
            "show_path": True,
            "show_time": True,
            "show_level": True,
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

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"

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
