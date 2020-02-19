from importlib import reload
from typing import Optional

import click
from bullet import Bullet, Input

from . import browser, models, shared
from .settings import settings


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
    launch_browser()
    try:
        run_loop()
    finally:
        quit_browser()


def launch_browser():
    if not settings.browser.name:
        cli = Bullet(
            prompt="\nSelect a browser for automation: ",
            bullet=" ● ",
            choices=browser.NAMES,
        )
        settings.browser.name = cli.launch().lower()

    if not settings.site.domain:
        domains = [p.domain for p in models.Page.objects.all()]  # type: ignore
        if domains:
            cli = Bullet(
                prompt="\nStarting domain: ", bullet=" ● ", choices=list(set(domains))
            )
        else:
            cli = Input(prompt="\nStarting domain: ", strip=True)
        settings.site.domain = cli.launch()

    shared.browser = browser.launch()
    browser.resize(shared.browser)
    shared.browser.visit(settings.site.url)


def quit_browser():
    if shared.browser:
        browser.save_size(shared.browser)
        shared.browser.quit()


def run_loop():
    page = models.autopage()
    while True:
        cli = Bullet(
            prompt=f"\n{page}\n\nSelect an action: ",
            bullet=" ● ",
            choices=[RELOAD] + dir(page),
        )
        action = cli.launch()
        if action == RELOAD:
            reload(models)
            page = models.autopage()
            continue

        cli = Input(prompt=f"\nValue: ")
        page = page.perform(action, prompt=cli.launch)


if __name__ == '__main__':  # pragma: no cover
    main()
