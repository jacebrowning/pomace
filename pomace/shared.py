from playwright.sync_api import Page

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
        assert isinstance(browser, PlaywrightBrowser)
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


client = _Client()
