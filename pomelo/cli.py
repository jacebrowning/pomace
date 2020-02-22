import os
from importlib import reload
from pathlib import Path
from typing import Optional

import click
from bullet import Bullet, Input

from . import browser, models, utils
from .config import settings


RELOAD = '<reload actions>'


@click.command()
@click.option('--name')
@click.option('--headless', is_flag=True)
@click.option('--domain')
@click.option('-r', '--root', type=Path)
def main(
    name: Optional[str] = '',
    headless: bool = False,
    domain: Optional[str] = '',
    root: Optional[Path] = None,
):
    if root:
        os.chdir(root)

    if name is not None:
        settings.browser.name = name.lower()

    settings.browser.headless = headless

    if domain is not None:
        settings.site.url = f'https://{domain}'

    launch_browser()
    try:
        run_loop()
    finally:
        utils.quit_browser()


def launch_browser():
    if not settings.browser.name:
        cli = Bullet(
            prompt="\nSelect a browser for automation: ",
            bullet=" ● ",
            choices=browser.NAMES,
        )
        settings.browser.name = cli.launch().lower()

    if not settings.site.domain:
        domains = [p.domain for p in models.Page.objects.all()]
        if domains:
            cli = Bullet(
                prompt="\nStarting domain: ", bullet=" ● ", choices=list(set(domains))
            )
        else:
            cli = Input(prompt="\nStarting domain: ", strip=True)
        settings.site.url = f'https://{cli.launch()}'

    utils.launch_browser()


def run_loop():
    page = models.autopage()
    clear_screen()
    print(page)
    while True:
        choices = [RELOAD] + dir(page)
        cli = Bullet(prompt=f"\nSelect an action: ", bullet=" ● ", choices=choices)
        action = cli.launch()
        if action == RELOAD:
            reload(models)
            page = models.autopage()
            clear_screen()
            print(page)
            continue

        cli = Input(prompt=f"\nValue: ")
        page, transitioned = page.perform(action, prompt=cli.launch)
        if transitioned:
            clear_screen()
            print(page)


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == '__main__':  # pragma: no cover
    main()
