import os
from typing import Tuple

from . import browser, enums, shared
from .config import settings


def browser_if_unset():
    if settings.browser.name:
        return

    if "CI" in os.environ or not shared.cli:
        settings.browser.name = os.getenv("BROWSER", "firefox")
        return

    command = shared.cli.Bullet(
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

    if "CI" in os.environ or not shared.cli:
        settings.url = "http://example.com"
        return

    if domains:
        command = shared.cli.Bullet(
            prompt="\nStarting domain: ", bullet=" ● ", choices=domains
        )
    else:
        command = shared.cli.Input(prompt="\nStarting domain: ", strip=True)
    value = command.launch()
    print()
    settings.url = f"https://{value}"


def secret_if_unset(name: str):
    if settings.get_secret(name, _log=False):
        return

    if "CI" in os.environ or not shared.cli:
        settings.set_secret(name, "<unset>")
        return

    command = shared.cli.Input(prompt=f"{name}: ")
    value = command.launch()
    print()
    settings.set_secret(name, value)


def mode_and_value() -> Tuple[str, str]:
    if not shared.cli:
        return "", ""

    choices = ["<cancel>"] + [mode.value for mode in enums.Mode]
    command = shared.cli.Bullet(
        prompt="\nSelect element locator: ",
        bullet=" ● ",
        choices=choices,
    )
    mode = command.launch()
    if mode == "<cancel>":
        print()
        return "", ""

    command = shared.cli.Input("\nValue to match: ")
    value = command.launch()
    print()
    return mode, value
