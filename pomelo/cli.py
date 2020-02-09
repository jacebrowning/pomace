from importlib import reload
from typing import List

import click
import log
from bullet import Bullet, Input

from . import browsers, models, shared
from .utils import autopage


RELOAD = '<relaod>'


@click.command()
@click.option('--name')
@click.option('--headless', is_flag=True)
@click.option('--domain')
def main(name: str = '', headless: bool = False, domain: str = ''):
    log.init()
    log.silence('datafiles')
    start_browser(name, headless, domain)
    try:
        run_loop()
    finally:
        quit_browser()


def start_browser(name: str = '', headless: bool = False, domain: str = ''):
    if not name:
        cli = Bullet(
            prompt="\nSelect a browser for automation: ",
            bullet=" ● ",
            choices=browsers.NAMES,
        )
        name = cli.launch()

    if not domain:
        cli = Input(prompt="\nStarting domain: ", strip=True)
        domain = cli.launch()

    shared.browser = browsers.get(name, headless)
    shared.browser.visit('http://' + domain)


def quit_browser():
    if shared.browser:
        shared.browser.quit()


def run_loop():
    while True:
        page = autopage()

        cli = Bullet(
            prompt=f"\n{page}\n\nSelect an action: ",
            bullet=" ● ",
            choices=actions(page),
        )
        action = cli.launch()
        if action == RELOAD:
            reload(models)
            continue

        cli = Input(prompt=f"\nValue: ")
        page.perform(action, prompt=cli.launch)


def actions(page: models.Page) -> List[str]:
    return [RELOAD, *[str(a) for a in page.actions]]


if __name__ == '__main__':  # pragma: no cover
    main()
