import click
import log
from bullet import Bullet, Input

from . import browsers, models


RELOAD = '<relaod>'


@click.command()
@click.option('--headless', is_flag=True)
def main(headless: bool = False):
    log.init()
    log.silence('datafiles')

    cli = Bullet(
        prompt="\nSelect a browser for automation: ",
        bullet=" ● ",
        choices=browsers.NAMES,
    )
    name = cli.launch()
    browser = browsers.get(name, headless)

    try:
        cli = Input(prompt="\nStarting domain: ", strip=True)
        domain = cli.launch()
        browser.visit('http://' + domain)
        loop(browser)
    finally:
        browser.quit()


def loop(browser: browsers.Browser):
    while True:
        page = models.Page.from_url(browser.url)

        cli = Bullet(
            prompt="\nSelect an action: ", bullet=" ● ", choices=[RELOAD, *page.actions]
        )
        action = cli.launch()
        if action == RELOAD:
            continue

        print()
        print(action)


if __name__ == '__main__':  # pragma: no cover
    main()
