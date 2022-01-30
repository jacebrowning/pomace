from typing import Callable, List

import log
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from .compat import Page
from .types import GenericBrowser, PlaywrightBrowser

__all__ = ["browser", "client", "linebreak"]

browser: GenericBrowser = None
linebreak: bool = True


class _Client:
    @property
    def windows(self):
        if isinstance(browser, PlaywrightBrowser):
            return []

        return browser.windows

    @property
    def page(self) -> Page:
        # Raises an AttributeError for non-Playwright browsers
        return browser.contexts[0].pages[0]

    @property
    def url(self) -> str:
        if browser is None:
            return ""

        if isinstance(browser, PlaywrightBrowser):
            self.page.bring_to_front()
            return self.page.url

        return browser.url

    @property
    def title(self) -> str:
        if isinstance(browser, PlaywrightBrowser):
            return self.page.title()

        return browser.title

    @property
    def html(self) -> str:
        if isinstance(browser, PlaywrightBrowser):
            return self.page.content()

        return browser.html

    @staticmethod
    def visit(url: str, size: dict) -> None:
        if isinstance(browser, PlaywrightBrowser):
            page = browser.new_page(screen=size, viewport=size)  # type: ignore
            page.goto(url)
        else:
            if browser.driver.get_window_size() != size:
                browser.driver.set_window_size(size["width"], size["height"])
                browser.driver.set_window_position(0, 0)
                size = browser.driver.get_window_size()
                log.debug(f"Resized browser: {size}")
            browser.visit(url)

    def type_key(self, name: str) -> Callable:
        if isinstance(browser, PlaywrightBrowser):
            key = name.capitalize()
            return lambda: self.page.keyboard.press(key)

        key = getattr(Keys, name.upper())
        return ActionChains(browser.driver).send_keys(key).perform

    def type_key_with_modifier(self, names: List[str]) -> Callable:
        if len(names) > 2:
            raise ValueError("Multiple modifier keys are not yet supported")

        if isinstance(browser, PlaywrightBrowser):
            keys = "+".join(name.capitalize() for name in names)
            return lambda: self.page.keyboard.press(keys)

        modifier = getattr(Keys, names[0].upper())
        key = getattr(Keys, names[1].upper())
        return (
            ActionChains(browser.driver)
            .key_down(modifier)
            .send_keys(key)
            .key_up(modifier)
            .perform
        )

    def execute(self, javascript: str):
        if isinstance(browser, PlaywrightBrowser):
            self.page.evaluate(javascript)
        else:
            browser.execute_script(javascript)

    @staticmethod
    def clear_cookies():
        log.info("Clearing cookies")
        if isinstance(browser, PlaywrightBrowser):
            browser.contexts[0].clear_cookies()
        else:
            browser.cookies.delete()


client = _Client()
