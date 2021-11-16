from typing import Callable, List

from playwright.sync_api import Page
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

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
        if isinstance(browser, PlaywrightBrowser):
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
    def visit(url: str) -> None:
        if isinstance(browser, PlaywrightBrowser):
            page = browser.new_page()
            page.goto(url)
        else:
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


client = _Client()
