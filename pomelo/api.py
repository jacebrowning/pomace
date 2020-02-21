import atexit

from . import models, utils
from .config import settings


def visit(url: str, *, browser: str = '') -> models.Page:
    settings.site.url = url
    if browser:
        settings.browser.name = browser.lower()

    atexit.register(utils.quit_browser)

    utils.launch_browser()

    return models.autopage()
