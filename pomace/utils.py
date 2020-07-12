import inspect
import os
import random
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
        if random.random() > 0.5:
            prefix, first_name, last_name = (
                self.prefix_female,
                self.first_name_female,
                self.last_name,
            )
        else:
            prefix, first_name, last_name = (
                self.prefix_male,
                self.first_name_male,
                self.last_name,
            )
        email_address = f'{first_name}{last_name}@{self.free_email_domain}'.lower()
        return Person(prefix, first_name, last_name, email_address, self.postcode)


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


def locate_models():
    cwd = Path.cwd()

    for frame in inspect.getouterframes(inspect.currentframe()):
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
