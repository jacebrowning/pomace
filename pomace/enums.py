import time
from enum import Enum

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

    def post_action(self):
        if self is self.FILL:
            element = shared.browser.driver.switch_to_active_element()
            element.send_keys(Keys.TAB)
        time.sleep(self.delay)
