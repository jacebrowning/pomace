import os
import sys
from functools import wraps
from importlib import import_module
from typing import Optional, Tuple, no_type_check

import log
from IPython import embed

from . import browser, enums, shared
from .config import settings


try:
    import bullet
except ImportError:
    bullet = None  # https://github.com/Mckinsey666/bullet/issues/2
    log.warn("Interactive CLI prompts not yet supported on Windows")

if "pytest" in sys.modules:
    bullet = None
    log.warn("Interactive CLI prompts disabled while testing")


RELOAD_ACTIONS = "<reload actions>"
ADD_ACTION = "<add action>"
CANCEL = "<cancel prompt>"
DEBUG = "<start shell>"


def linebreak(*, force: bool = False):
    if not shared.linebreak or force:
        print()
        shared.linebreak = True


def offset(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        linebreak()
        value = function(*args, **kwargs)
        linebreak()
        return value

    return wrapper


@offset
def browser_if_unset():
    if settings.browser.name:
        return

    if "CI" in os.environ or not bullet:
        value = os.getenv("BROWSER") or browser.NAMES[0]
        settings.browser.name = value.lower()
        return

    shared.linebreak = False
    command = bullet.Bullet(
        prompt="Select a browser for automation: ",
        bullet=" ● ",
        choices=browser.NAMES,
    )
    settings.browser.name = command.launch()


@offset
def url_if_unset(domains=None):
    if settings.url:
        return

    if "CI" in os.environ or not bullet:
        settings.url = "http://example.com"
        return

    shared.linebreak = False
    if domains:
        command = bullet.Bullet(
            prompt="Starting domain: ", bullet=" ● ", choices=domains
        )
    else:
        command = bullet.Input(prompt="Starting domain: ", strip=True)
    value = command.launch()
    settings.url = f"https://{value}"


@offset
def secret_if_unset(name: str):
    if settings.get_secret(name, _log=False):
        return

    if "CI" in os.environ or not bullet:
        settings.set_secret(name, "<unset>")
        return

    value = named_value(name)
    settings.set_secret(name, value)


@offset
def action(page) -> Optional[str]:
    shared.linebreak = False
    choices = [RELOAD_ACTIONS] + dir(page) + [DEBUG, ADD_ACTION]
    command = bullet.Bullet(
        prompt="Select an action: ",
        bullet=" ● ",
        choices=choices,
    )
    value = command.launch()

    if value == RELOAD_ACTIONS:
        return None

    if value == DEBUG:
        shell()
        return ""

    if value == ADD_ACTION:
        verb, name = verb_and_name()
        if verb and name:
            return f"{verb}_{name}"
        return ""

    return value


@offset
def named_value(name: str) -> Optional[str]:
    if not bullet:
        return None

    shared.linebreak = False
    command = bullet.Input(prompt="Value for " + name.replace("_", " ") + ": ")
    value = command.launch()
    return value


@offset
def verb_and_name() -> Tuple[str, str]:
    choices = [CANCEL] + [verb.value for verb in enums.Verb] + [DEBUG]
    command = bullet.Bullet(
        prompt="Select element verb: ",
        bullet=" ● ",
        choices=choices,
    )
    verb = command.launch()
    linebreak(force=True)

    if verb == CANCEL:
        return "", ""

    if verb == DEBUG:
        shell()
        return "", ""

    shared.linebreak = False
    command = bullet.Input("Name of element: ")
    name = command.launch().lower().replace(" ", "_")
    return verb, name


@offset
def mode_and_value() -> Tuple[str, str]:
    if not bullet:
        return "", ""

    choices = [CANCEL] + [mode.value for mode in enums.Mode] + [DEBUG]
    command = bullet.Bullet(
        prompt="Select element locator: ",
        bullet=" ● ",
        choices=choices,
    )
    mode = command.launch()
    linebreak(force=True)

    if mode == CANCEL:
        return "", ""

    if mode == DEBUG:
        shell()
        return "", ""

    shared.linebreak = False
    command = bullet.Input("Value to match: ")
    value = command.launch()
    return mode, value


@no_type_check
def shell():
    linebreak()

    pomace = import_module("pomace")
    globals().update(
        {name: getattr(pomace.models, name) for name in pomace.models.__all__}
    )
    globals().update(
        {name: getattr(pomace.types, name) for name in pomace.types.__all__}
    )
    auto = pomace.models.auto

    page = auto()  # pylint: disable=unused-variable
    embed(colors="neutral")
