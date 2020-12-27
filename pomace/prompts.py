import os
import sys
from functools import wraps
from typing import Optional, Tuple

import log

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
CANCEL = "<cancel>"


def linebreak(*, force: bool = False):
    if not shared.linebreak or force:
        print()
        shared.linebreak = True


def include_linebreaks(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        linebreak()
        value = function(*args, **kwargs)
        linebreak()
        return value

    return wrapper


@include_linebreaks
def browser_if_unset():
    if settings.browser.name:
        return

    if "CI" in os.environ or not bullet:
        settings.browser.name = os.getenv("BROWSER", "firefox")
        return

    shared.linebreak = False
    command = bullet.Bullet(
        prompt="Select a browser for automation: ",
        bullet=" ● ",
        choices=browser.NAMES,
    )
    value = command.launch()
    settings.browser.name = value.lower()


@include_linebreaks
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


@include_linebreaks
def secret_if_unset(name: str):
    if settings.get_secret(name, _log=False):
        return

    if "CI" in os.environ or not bullet:
        settings.set_secret(name, "<unset>")
        return

    value = named_value(name)
    settings.set_secret(name, value)


@include_linebreaks
def action(page) -> Optional[str]:
    shared.linebreak = False
    choices = [RELOAD_ACTIONS] + dir(page) + [ADD_ACTION]
    command = bullet.Bullet(
        prompt="Select an action: ",
        bullet=" ● ",
        choices=choices,
    )
    value = command.launch()

    if value == RELOAD_ACTIONS:
        return None

    if value == ADD_ACTION:
        verb, name = verb_and_name()
        return f"{verb}_{name}"

    return value


@include_linebreaks
def named_value(name: str) -> Optional[str]:
    if not bullet:
        return None

    shared.linebreak = False
    command = bullet.Input(prompt="Value for " + name.replace("_", " ") + ": ")
    value = command.launch()
    return value


@include_linebreaks
def verb_and_name() -> Tuple[str, str]:
    choices = [verb.value for verb in enums.Verb]
    command = bullet.Bullet(
        prompt="Select element verb: ",
        bullet=" ● ",
        choices=choices,
    )
    verb = command.launch()
    linebreak(force=True)

    shared.linebreak = False
    command = bullet.Input("Name of element: ")
    name = command.launch().lower().replace(" ", "_")
    return verb, name


@include_linebreaks
def mode_and_value() -> Tuple[str, str]:
    if not bullet:
        return "", ""

    choices = [CANCEL] + [mode.value for mode in enums.Mode]
    command = bullet.Bullet(
        prompt="Select element locator: ",
        bullet=" ● ",
        choices=choices,
    )
    mode = command.launch()
    linebreak(force=True)

    if mode == CANCEL:
        return "", ""

    shared.linebreak = False
    command = bullet.Input("Value to match: ")
    value = command.launch()
    return mode, value
