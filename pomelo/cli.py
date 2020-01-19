"""A sample CLI."""

import click
import log
from IPython import start_ipython


@click.command()
def main():
    log.init()
    start_ipython()


if __name__ == '__main__':  # pragma: no cover
    main()
