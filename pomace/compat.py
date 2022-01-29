try:
    # pylint: disable=unused-import
    from playwright.sync_api import Browser as PlaywrightBrowser
    from playwright.sync_api import ElementHandle
    from playwright.sync_api import ElementHandle as PlaywrightElement
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import Page
    from playwright.sync_api import sync_playwright as playwright
except ImportError:
    PlaywrightBrowser = None  # type: ignore
    ElementHandle = None  # type: ignore
    PlaywrightElement = None  # type: ignore
    PlaywrightError = None  # type: ignore
    Page = None  # type: ignore
    playwright = None  # type: ignore
