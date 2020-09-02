import inspect
import os
import time
from pathlib import Path

import faker
import log

from . import browser, shared
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


def launch_browser(delay: float = 0.0) -> bool:
    launched = False
    if not shared.browser:
        shared.browser = browser.launch()
        browser.resize(shared.browser)
        launched = True
    shared.browser.visit(settings.url)
    time.sleep(delay)
    return launched


def quit_browser(silence_logging: bool = False):
    if silence_logging:
        log.silence('pomace', 'selenium', allow_warning=True)
    try:
        browser.save_url(shared.browser)
        browser.save_size(shared.browser)
        shared.browser.quit()
    except Exception as e:
        log.debug(e)


def locate_models(*, caller=None):
    cwd = Path.cwd()

    if caller:
        for frame in inspect.getouterframes(caller):
            if 'pomace' not in frame.filename or 'pomace/tests' in frame.filename:
                path = Path(frame.filename)
                log.debug(f"Found caller's package directory: {path.parent}")
                os.chdir(path.parent)
                return

    if (cwd / 'sites').is_dir():
        log.debug(f"Found models in current directory: {cwd}")
        return

    for path in cwd.iterdir():
        if (path / 'sites').is_dir():
            log.debug(f"Found models in package directory: {path}")
            os.chdir(path)
            return
