import atexit
import inspect
from typing import Optional

import log

from . import cli, models, utils
from .config import settings


__all__ = ['fake', 'prompt', 'visit']


fake = utils.Fake()


def visit(
    url: str = '',
    *,
    browser: str = '',
    headless: Optional[bool] = None,
    delay: float = 0.0,
) -> models.Page:
    if url:
        settings.url = url
    else:
        cli.prompt_for_url_if_unset()

    if browser:
        settings.browser.name = browser.lower()
    else:
        cli.prompt_for_browser_if_unset()

    if headless is not None:
        settings.browser.headless = headless

    if utils.launch_browser(delay):
        log.silence('urllib3.connectionpool')
        atexit.register(utils.quit_browser, silence_logging=True)

    utils.locate_models(caller=inspect.currentframe())

    return models.autopage()


def prompt(*names):
    for name in names:
        cli.prompt_for_secret_if_unset(name)
    return settings
