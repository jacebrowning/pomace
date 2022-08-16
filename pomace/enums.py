import time
from enum import Enum
from typing import Callable, Iterator, Optional, Tuple

import inflection
import log
from selenium.webdriver.common.keys import Keys

from . import shared
from .types import GenericElement, PlaywrightBrowser


class Mode(Enum):

    NAME = "name"
    ID = "id"
    TEXT = "text"
    PARTIAL_TEXT = "text (partial)"  # extended
    VALUE = "value"
    ARIA_LABEL = "aria-label"  # extended
    CSS = "css"
    TAG = "tag"
    XPATH = "xpath"

    @property
    def finder(self) -> Callable:
        if isinstance(shared.browser, PlaywrightBrowser):
            return shared.client.page.query_selector_all

        if self is self.PARTIAL_TEXT:
            return shared.browser.links.find_by_partial_text

        if self is self.ARIA_LABEL:
            return shared.browser.find_by_css

        return getattr(shared.browser, f"find_by_{self.value}")

    def find(self, value) -> GenericElement:
        if self is self.ARIA_LABEL:
            value = f'[aria-label="{value}"]'
        elif isinstance(shared.browser, PlaywrightBrowser):
            if self is self.TEXT:
                value = f"text={value!r}"
            elif self is self.PARTIAL_TEXT:
                value = f"text={value}"
            elif self in [self.ID]:
                value = f"{self.value}={value}"
            elif self not in [self.CSS, self.XPATH]:
                value = f"[{self.value}={value!r}]"
        return self.finder(value)


class Verb(Enum):
    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    CHOOSE = "choose"
    TYPE = "type"

    @property
    def humanized(self) -> str:
        return (self.value.capitalize() + "ing").replace("eing", "ing")

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

    def get_default_locators(self, name: str) -> Iterator[Tuple[str, str]]:
        if self is self.CLICK:
            yield Mode.TEXT.value, inflection.titleize(name)
            yield Mode.TEXT.value, inflection.humanize(name)
            yield Mode.TEXT.value, name.replace("_", " ")
            yield Mode.VALUE.value, inflection.titleize(name)
            yield Mode.VALUE.value, inflection.humanize(name)
            yield Mode.VALUE.value, name.replace("_", " ")
            yield Mode.PARTIAL_TEXT.value, inflection.titleize(name)
            yield Mode.PARTIAL_TEXT.value, inflection.humanize(name)
            yield Mode.PARTIAL_TEXT.value, name.replace("_", " ")
        elif self in {self.FILL, self.SELECT}:
            yield Mode.NAME.value, name
            yield Mode.NAME.value, inflection.dasherize(name)
            yield Mode.ID.value, name
            yield Mode.ID.value, inflection.dasherize(name)
            yield Mode.ARIA_LABEL.value, inflection.titleize(name)
            yield Mode.CSS.value, f'[placeholder="{inflection.titleize(name)}"]'
            yield Mode.ID.value, inflection.titleize(name).replace(" ", "")

    def pre_action(self):
        if self is self.CLICK:
            shared.client.execute(
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
        start: float = 0.0,
    ):
        start = start or time.time()

        if delay:
            log.info(f"Waiting {delay} seconds before continuing")
            time.sleep(delay)
            start += delay

        if wait is None:
            wait = 0.0 if self.updates else 5.0
        if wait:
            log.debug(f"Waiting {wait} seconds for URL to change from {previous_url}")

        elapsed = 0.0
        logged = False
        while elapsed < wait:
            time.sleep(0.1)
            elapsed = round(time.time() - start, 1)
            current_url = shared.client.url
            if current_url != previous_url:
                log.debug(f"URL changed after {elapsed} seconds to {current_url}")
                time.sleep(delay or 0.5)
                break
            if elapsed > 1.0 and not logged:
                log.info(f"Waiting up to {wait} seconds for the URL to change")
                logged = True
