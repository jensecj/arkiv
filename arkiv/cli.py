import logging, logging.config

import click

from . import config as CFG
from .core import archive

log = logging.getLogger(__name__)


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    version = open("__version__.py", "r").read().strip()
    print(f"arkiv v{version}")
    ctx.exit()


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("url", type=str)
@click.option("-v", "--verbose", help="", count=True)
@click.option("-V", "--version", is_flag=True, callback=print_version, expose_value=False, is_eager=True,)
def main(url, verbose):
    verbosity = {
        0: {"root": {"handlers": ["default"], "level": "INFO"}},
        1: {"root": {"handlers": ["extended"], "level": "INFO"}},
        2: {"root": {"handlers": ["extended"], "level": "DEBUG"}},
    }
    CFG.LOG_CONFIG.update(verbosity.get(verbose))
    logging.config.dictConfig(CFG.LOG_CONFIG)

    config = CFG.load()

    archive(config, url)


if __name__ == "__main__":
    main()