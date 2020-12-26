import os
import sys
from typing import Optional, Tuple

import log

from . import browser, enums
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
CANCEL = "<cancel>"


def browser_if_unset():
    if settings.browser.name:
        return

    if "CI" in os.environ or not bullet:
        settings.browser.name = os.getenv("BROWSER", "firefox")
        return

    command = bullet.Bullet(
        prompt="\nSelect a browser for automation: ",
        bullet=" ● ",
        choices=browser.NAMES,
    )
    value = command.launch()
    print()
    settings.browser.name = value.lower()


def url_if_unset(domains=None):
    if settings.url:
        return

    if "CI" in os.environ or not bullet:
        settings.url = "http://example.com"
        return

    if domains:
        command = bullet.Bullet(
            prompt="\nStarting domain: ", bullet=" ● ", choices=domains
        )
    else:
        command = bullet.Input(prompt="\nStarting domain: ", strip=True)
    value = command.launch()
    print()
    settings.url = f"https://{value}"


def secret_if_unset(name: str):
    if settings.get_secret(name, _log=False):
        return

    if "CI" in os.environ or not bullet:
        settings.set_secret(name, "<unset>")
        return

    command = bullet.Input(prompt=f"{name}: ")
    value = command.launch()
    print()
    settings.set_secret(name, value)


def action(page) -> Optional[str]:
    choices = [RELOAD_ACTIONS] + dir(page)
    command = bullet.Bullet(
        prompt="\nSelect an action: ", bullet=" ● ", choices=choices
    )
    value = command.launch()
    print()
    return None if value == RELOAD_ACTIONS else value


def named_value(name: str) -> Optional[str]:
    if not bullet:
        return None

    command = bullet.Input(prompt="Value for " + name.replace("_", " ") + ": ")
    value = command.launch()
    return value


def mode_and_value() -> Tuple[str, str]:
    if not bullet:
        return "", ""

    choices = [CANCEL] + [mode.value for mode in enums.Mode]
    command = bullet.Bullet(
        prompt="\nSelect element locator: ",
        bullet=" ● ",
        choices=choices,
    )
    mode = command.launch()
    if mode == CANCEL:
        print()
        return "", ""

    command = bullet.Input("\nValue to match: ")
    value = command.launch()
    print()
    return mode, value
