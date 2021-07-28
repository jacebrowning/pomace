import inspect
from typing import Optional

import log

from . import models, prompts, types, utils
from .config import settings
from .models import Page, auto


__all__ = [
    "auto",
    "clean",
    "fake",
    "freeze",
    "log",
    "Page",
    "prompt",
    "visit",
]


fake = types.Fake()


def visit(
    url: str = "",
    *,
    browser: str = "",
    headless: Optional[bool] = None,
    delay: float = 0.0,
) -> models.Page:
    if url:
        settings.url = url
    else:
        prompts.url_if_unset()

    if browser:
        settings.browser.name = browser.lower()
    else:
        prompts.browser_if_unset()

    if headless is not None:
        settings.browser.headless = headless

    utils.launch_browser(delay, silence_logging=True)
    utils.locate_models(caller=inspect.currentframe())

    return models.auto()


def prompt(*names):
    for name in names:
        prompts.secret_if_unset(name)
    return settings


def freeze():
    log.debug("Disabling interactive prompts and automatic locators")
    prompts.bullet = None
    settings.dev = False


def clean():
    utils.locate_models(caller=inspect.currentframe())
    for page in models.Page.objects.all():
        page.clean(force=True)
