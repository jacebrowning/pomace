import time

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
        first, last = self.first_name, self.last_name
        email = f'{first}{last}@{self.free_email_domain}'.lower()
        return Person(first, last, email, self.postcode)


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
