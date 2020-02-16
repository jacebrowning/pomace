from importlib import reload
from typing import List, Optional

import click
from bullet import Bullet, Input

from . import browsers, models, shared
from .settings import settings
from .utils import autopage


RELOAD = '<relaod>'


@click.command()
@click.option('--name')
@click.option('--headless', is_flag=True)
@click.option('--domain')
def main(name: Optional[str] = '', headless: bool = False, domain: Optional[str] = ''):
    if name is not None:
        settings.browser.name = name.lower()
    settings.browser.headless = headless
    if domain is not None:
        settings.site.domain = domain
    start_browser()
    try:
        run_loop()
    finally:
        quit_browser()


def start_browser():
    if not settings.browser.name:
        cli = Bullet(
            prompt="\nSelect a browser for automation: ",
            bullet=" ● ",
            choices=browsers.NAMES,
        )
        settings.browser.name = cli.launch().lower()

    if not settings.site.domain:
        cli = Input(prompt="\nStarting domain: ", strip=True)
        settings.site.domain = cli.launch()

    shared.browser = browsers.get(settings.browser.name, settings.browser.headless)
    shared.browser.visit('http://' + settings.site.domain)


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
