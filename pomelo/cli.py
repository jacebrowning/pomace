from importlib import reload

import click
import log
from bullet import Bullet, Input

from . import browsers, models


RELOAD = '<relaod>'


@click.command()
@click.option('--name')
@click.option('--headless', is_flag=True)
@click.option('--domain')
def main(name: str = '', headless: bool = False, domain: str = ''):
    log.init()
    log.silence('datafiles')

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

    browser = browsers.get(name, headless)
    try:
        browser.visit('http://' + domain)
        loop(browser)
    finally:
        browser.quit()


def loop(browser: browsers.Browser):
    while True:
        page = models.Page.from_url(browser.url)

        cli = Bullet(
            prompt="\nSelect an action: ",
            bullet=" ● ",
            choices=[RELOAD, *page.action_names],
        )
        action = cli.launch()
        if action == RELOAD:
            reload(models)
            continue

        print(f'\nTODO: {action}')


if __name__ == '__main__':  # pragma: no cover
    main()
