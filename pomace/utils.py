import inspect
import os
import time
from pathlib import Path

import faker
import log

from . import browser, models, shared
from .config import settings
from .types import Person


class Fake:
    def __init__(self):
        self.generator = faker.Faker()

    def __getattr__(self, name):
        method = getattr(self.generator, name)
        return method()

    @property
    def person(self) -> Person:
        return Person.random(self)

    @property
    def zip_code(self) -> str:
        return self.generator.postcode()


def prompt_for_browser_if_unset():
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


def prompt_for_url_if_unset():
    if settings.url:
        return

    if "CI" in os.environ or not shared.cli:
        settings.url = "http://example.com"
        return

    domains = [p.domain for p in models.Page.objects.all()]
    if domains:
        command = shared.cli.Bullet(
            prompt="\nStarting domain: ", bullet=" ● ", choices=list(set(domains))
        )
    else:
        command = shared.cli.Input(prompt="\nStarting domain: ", strip=True)
    value = command.launch()
    print()
    settings.url = f"https://{value}"


def prompt_for_secret_if_unset(name: str):
    if settings.get_secret(name, _log=False):
        return

    if "CI" in os.environ or not shared.cli:
        settings.set_secret(name, "<unset>")
        return

    command = shared.cli.Input(prompt=f"{name}: ")
    value = command.launch()
    print()
    settings.set_secret(name, value)


def launch_browser(delay: float = 0.0) -> bool:
    did_launch = False

    if not shared.browser:
        shared.browser = browser.launch()
        browser.resize(shared.browser)
        did_launch = True

    shared.browser.visit(settings.url)
    time.sleep(delay)

    return did_launch


def quit_browser(*, silence_logging: bool = False) -> bool:
    did_quit = False

    if silence_logging:
        log.silence("pomace", "selenium", allow_warning=True)

    if shared.browser:
        try:
            browser.save_url(shared.browser)
            browser.save_size(shared.browser)
            shared.browser.quit()
        except Exception as e:
            log.debug(e)
        else:
            did_quit = True

    return did_quit


def locate_models(*, caller=None):
    cwd = Path.cwd()

    if caller:
        for frame in inspect.getouterframes(caller):
            if "pomace" not in frame.filename or "pomace/tests" in frame.filename:
                path = Path(frame.filename)
                log.debug(f"Found caller's package directory: {path.parent}")
                os.chdir(path.parent)
                return

    if (cwd / "sites").is_dir():
        log.debug(f"Found models in current directory: {cwd}")
        return

    for path in cwd.iterdir():
        if (path / "sites").is_dir():
            log.debug(f"Found models in package directory: {path}")
            os.chdir(path)
            return
