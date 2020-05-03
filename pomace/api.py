import atexit

import log

from . import cli, models, utils
from .config import settings


def visit(url: str = '', *, browser: str = '', delay: float = 0.0) -> models.Page:
    if url:
        settings.url = url
    else:
        cli.prompt_for_url_if_unset()

    if browser:
        settings.browser.name = browser.lower()
    else:
        cli.prompt_for_browser_if_unset()

    if utils.launch_browser(delay):
        log.silence('urllib3.connectionpool')
        atexit.register(utils.quit_browser)

    return models.autopage()


def prompt(*names):
    for name in names:
        cli.prompt_for_secret_if_unset(name)
    return settings
