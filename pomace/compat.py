"""Compatibility layer to handle systems that cannot run Playwright."""

# pylint: disable=unused-import
# mypy: ignore-errors

import sys

try:

    from playwright.sync_api import Browser as PlaywrightBrowser
    from playwright.sync_api import ElementHandle
    from playwright.sync_api import ElementHandle as PlaywrightElement
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import Page
    from playwright.sync_api import sync_playwright as playwright

    if "pytest" in sys.modules:
        raise ImportError

except (ImportError, AttributeError):

    class Missing:
        def __bool__(self):
            return False

    PlaywrightBrowser = Missing
    ElementHandle = Missing
    PlaywrightElement = Missing
    PlaywrightError = None
    Page = Missing
    playwright = Missing
