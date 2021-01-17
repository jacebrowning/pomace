import time
from enum import Enum
from typing import Iterator, Optional, Tuple

import inflection
import log
from selenium.webdriver.common.keys import Keys

from . import shared


class Mode(Enum):

    NAME = "name"
    ID = "id"
    TEXT = "text"
    PARTIAL_TEXT = "partial_text"
    VALUE = "value"
    CSS = "css"
    TAG = "tag"
    XPATH = "xpath"

    @property
    def finder(self):
        if self is self.PARTIAL_TEXT:
            return getattr(shared.browser.links, f"find_by_{self.value}")
        return getattr(shared.browser, f"find_by_{self.value}")


class Verb(Enum):
    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    CHOOSE = "choose"
    TYPE = "type"

    @classmethod
    def validate(cls, value: str, name: str) -> bool:
        values = [enum.value for enum in cls]
        if value not in values:
            return False
        # TODO: name should be validated somewhere else
        if value == "type" and not all(
            hasattr(Keys, n.upper()) for n in name.split("_")
        ):
            return False
        return True

    @property
    def updates(self) -> bool:
        return self not in {self.CLICK, self.TYPE}

    @property
    def wait(self) -> float:
        if self in {self.CLICK}:
            return 2.0
        if self in {self.TYPE}:
            return 1.0
        return 0.0

    def get_default_locators(self, name: str) -> Iterator[Tuple[str, str]]:
        if self is self.CLICK:
            yield Mode.TEXT.value, inflection.titleize(name)
            yield Mode.TEXT.value, inflection.humanize(name)
            yield Mode.TEXT.value, name.replace("_", " ")
            yield Mode.VALUE.value, inflection.titleize(name)
            yield Mode.VALUE.value, inflection.humanize(name)
            yield Mode.VALUE.value, name.replace("_", " ")
        elif self in {self.FILL, self.SELECT}:
            yield Mode.NAME.value, name
            yield Mode.NAME.value, inflection.dasherize(name)
            yield Mode.ID.value, name
            yield Mode.ID.value, inflection.dasherize(name)
            yield Mode.CSS.value, f'[aria-label="{inflection.titleize(name)}"]'
            yield Mode.ID.value, inflection.titleize(name).replace(" ", "")

    def pre_action(self):
        if self is self.CLICK:
            shared.browser.execute_script(
                """
                Array.from(document.querySelectorAll('a[target="_blank"]'))
                .forEach(link => link.removeAttribute('target'));
                """
            )

    def post_action(
        self,
        previous_url: str,
        delay: float = 0.0,
        wait: Optional[float] = None,
    ):
        if delay:
            log.debug(f"Waiting {delay} seconds before continuing")
            time.sleep(delay)

        if wait is None:
            wait = self.wait
        if wait:
            log.debug(f"Waiting {wait} seconds for URL to change: {previous_url}")

        elapsed = 0.0
        start = time.time()
        while elapsed < wait:
            time.sleep(0.1)
            elapsed = round(time.time() - start, 1)
            current_url = shared.browser.url
            if current_url != previous_url:
                log.debug(f"URL changed after {elapsed} seconds: {current_url}")
                break
