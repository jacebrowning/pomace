import atexit

from bullet import Input

from . import models, shared, utils
from .config import settings
from .types import URL


def visit(url: str, *, browser: str = '') -> models.Page:
    settings.url = url
    if browser:
        settings.browser.name = browser.lower()

    atexit.register(utils.quit_browser)

    utils.launch_browser()

    return models.autopage()


def get_secret(name: str) -> str:
    domain = URL(shared.browser.url).domain
    cli = Input(prompt=f"{domain} {name}: ")
    value = settings.get_secret(name) or cli.launch()
    settings.set_secret(name, value)
    return value
