import click
import log
from bullet import Bullet, Input

from . import browsers, models


@click.command()
def main():
    log.init()
    log.silence('datafiles')

    cli = Bullet(
        prompt="\nSelect a browser for automation: ",
        bullet=" ● ",
        choices=browsers.NAMES,
    )
    name = cli.launch()
    browser = browsers.get(name)

    try:
        cli = Input(prompt="\nStarting domain: ", strip=True)
        domain = cli.launch()
        browser.visit('http://' + domain)

        page = models.Page.from_url(browser.url)

        print()
        print(page)
    finally:
        browser.quit()


if __name__ == '__main__':  # pragma: no cover
    main()
