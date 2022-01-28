import subprocess
import sys

import log
import splinter
from fake_useragent import UserAgent, utils
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright
from splinter.exceptions import DriverNotFoundError
from webdriver_manager import chrome, firefox

from . import patched
from .config import settings
from .types import GenericBrowser, PlaywrightBrowser, SplinterBrowser

__all__ = ["launch", "resize", "save_url", "save_size", "close"]


NAMES = ["Firefox", "Chrome"]

PLAYWRIGHT_BROWSERS = {"chrome": "chromium"}

WEBDRIVER_MANAGERS = {
    "chromedriver": chrome.ChromeDriverManager,
    "geckodriver": firefox.GeckoDriverManager,
}

FALLBACK_USER_AGENT = "Mozilla/5.0 Gecko/20100101 Firefox/53.0"


def launch() -> GenericBrowser:
    if not settings.browser.name:
        sys.exit("No browser specified")

    if settings.browser.name == "open":
        settings.browser.name = NAMES[0]

    settings.framework = settings.framework.lower()
    settings.browser.name = settings.browser.name.lower()

    log.info(f"Launching {settings.browser.name!r} using {settings.framework!r}")
    try:
        function = LAUNCHERS[settings.framework]
    except KeyError:
        raise ValueError(f"Unsupported framework: {settings.framework}") from None
    else:
        return function(settings.browser.name, settings.browser.headless)


def launch_playwright_browser(name: str, headless: bool) -> PlaywrightBrowser:
    name = PLAYWRIGHT_BROWSERS.get(name, name)
    playwright = sync_playwright().start()
    try:
        browser = getattr(playwright, name)
    except AttributeError:
        sys.exit(f"Unsupported browser: {name}")

    try:
        instance = browser.launch(headless=headless)
    except PlaywrightError as e:
        if "playwright install" not in str(e):
            raise e from None
        subprocess.run((sys.executable, "-m", "playwright", "install", name))
        instance = browser.launch(headless=headless)

    setattr(instance, "_playwright", playwright)
    return instance


def launch_splinter_browser(name: str, headless: bool) -> SplinterBrowser:
    utils.get_browsers = patched.get_browsers
    options = {
        "headless": headless,
        "user_agent": UserAgent(fallback=FALLBACK_USER_AGENT)[name],
        "wait_time": 1.0,
    }
    log.debug(f"Options: {options}")
    try:
        return splinter.Browser(name, **options)
    except DriverNotFoundError:
        sys.exit(f"Unsupported browser: {name}")
    except Exception as e:  # pylint: disable=broad-except
        log.debug(str(e))

        if "exited process" in str(e):
            sys.exit("Browser update prevented launch. Please try again.")

        for driver, manager in WEBDRIVER_MANAGERS.items():
            if driver in str(e).lower():
                options["executable_path"] = manager().install()
                return splinter.Browser(name, **options)

        raise e from None


LAUNCHERS = {
    "playwright": launch_playwright_browser,
    "splinter": launch_splinter_browser,
}


def resize(browser: GenericBrowser):
    if isinstance(browser, PlaywrightBrowser):
        log.warn("Resizing Playwright browsers is not yet supported")
        return

    browser.driver.set_window_size(settings.browser.width, settings.browser.height)
    browser.driver.set_window_position(0, 0)
    size = browser.driver.get_window_size()
    log.debug(f"Resized browser: {size}")


def save_url(browser: GenericBrowser):
    if isinstance(browser, PlaywrightBrowser):
        page = browser.contexts[0].pages[0]
        url = page.url
    else:
        url = browser.url

    if "://" in url and settings.url != url:
        log.debug(f"Saving last browser URL: {url}")
        settings.url = url


def save_size(browser: GenericBrowser):
    if isinstance(browser, PlaywrightBrowser):
        log.warn("Resizing Playwright browsers is not yet supported")
        return

    size = browser.driver.get_window_size()
    if size != (settings.browser.width, settings.browser.height):
        log.debug(f"Saving last browser size: {size}")
        settings.browser.width = size["width"]
        settings.browser.height = size["height"]


def close(browser: GenericBrowser):
    if isinstance(browser, PlaywrightBrowser):
        browser.close()
        getattr(browser, "_playwright").stop()
    else:
        browser.quit()
