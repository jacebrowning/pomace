from .types import GenericBrowser, PlaywrightBrowser


browser: GenericBrowser = None
linebreak: bool = True


def get_url() -> str:
    if isinstance(browser, PlaywrightBrowser):
        context = browser.contexts[0]
        page = context.pages[0]
        return page.url

    return browser.url


def visit(url: str) -> None:
    if isinstance(browser, PlaywrightBrowser):
        page = browser.new_page()
        page.goto(url)
    else:
        browser.visit(url)
