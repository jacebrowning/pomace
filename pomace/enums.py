import time
from enum import Enum
from typing import Iterator, Tuple

import inflection
from selenium.webdriver.common.keys import Keys

from . import shared


class Mode(Enum):

    CSS = 'css'
    XPATH = 'xpath'
    TAG = 'tag'
    NAME = 'name'
    TEXT = 'text'
    PARTIAL_TEXT = 'partial_text'
    ID = 'id'
    VALUE = 'value'

    @property
    def finder(self):
        if self is self.PARTIAL_TEXT:
            return getattr(shared.browser.links, f'find_by_{self.value}')
        return getattr(shared.browser, f'find_by_{self.value}')


class Verb(Enum):
    CLICK = 'click'
    FILL = 'fill'
    SELECT = 'select'
    CHOOSE = 'choose'

    @classmethod
    def validate(cls, value: str) -> bool:
        return value in [e.value for e in cls]

    @property
    def updates(self) -> bool:
        return self not in {self.CLICK}

    @property
    def delay(self) -> float:
        if self in {self.CLICK}:
            return 1.0
        return 0.0

    def get_default_locators(self, name: str) -> Iterator[Tuple[str, str]]:
        if self is self.CLICK:
            yield Mode.TEXT.value, inflection.titleize(name)
            yield Mode.TEXT.value, inflection.humanize(name)
        elif self is self.FILL:
            yield Mode.NAME.value, name
            yield Mode.NAME.value, inflection.dasherize(name)
            yield Mode.ID.value, name
            yield Mode.ID.value, inflection.dasherize(name)
            yield Mode.CSS.value, f'[aria-label="{inflection.titleize(name)}"]'

    def post_action(self, *, delay: float = 0.0):
        if self is self.FILL:
            element = shared.browser.driver.switch_to.active_element
            element.send_keys(Keys.TAB)
        time.sleep(delay or self.delay)
