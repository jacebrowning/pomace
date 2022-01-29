import platform
import subprocess
import sys

import log
import splinter
from fake_useragent import UserAgent, utils
from splinter.exceptions import DriverNotFoundError
from webdriver_manager import chrome, firefox

from . import patched
from .compat import PlaywrightError, playwright
from .config import settings
from .types import GenericBrowser, PlaywrightBrowser, SplinterBrowser

__all__ = ["launch", "save_url", "save_size", "close"]


NAMES = ["Firefox", "Chrome"]

PLAYWRIGHT_BROWSERS = {"chrome": "chromium"}

WEBDRIVER_MANAGERS = {
    "chromedriver": chrome.ChromeDriverManager,
    "geckodriver": firefox.GeckoDriverManager,
}

FALLBACK_USER_AGENT = "Mozilla/5.0 Gecko/20100101 Firefox/53.0"


def launch() -> GenericBrowser:
    if not settings.browser.name:
        log.error("No browser specified")
        sys.exit(1)

    if settings.browser.name == "open":
        settings.browser.name = NAMES[0]

    settings.framework = settings.framework.lower()
    settings.browser.name = settings.browser.name.lower()

    log.info(f"Launching {settings.browser.name!r} using {settings.framework!r}")
    try:
        function = LAUNCHERS[settings.framework]
    except KeyError:
        log.error(f"Unsupported framework: {settings.framework}")
        sys.exit(1)

    return function(settings.browser.name, settings.browser.headless)


def launch_playwright_browser(name: str, headless: bool) -> PlaywrightBrowser:
    name = PLAYWRIGHT_BROWSERS.get(name, name)
    _playwright = playwright().start()
    try:
        browser = getattr(_playwright, name)
    except AttributeError:
        log.error(f"Unsupported browser: {name}")
        sys.exit(1)

    try:
        instance = browser.launch(headless=headless)
    except PlaywrightError as e:
        if "playwright install" not in str(e):
            raise e from None  # pylint: disable=raising-bad-type
        subprocess.run((sys.executable, "-m", "playwright", "install", name))
        instance = browser.launch(headless=headless)

    setattr(instance, "_playwright", _playwright)
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
        log.error(f"Unsupported browser: {name}")
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        log.debug(str(e))

        if "exited process" in str(e):
            log.error("Browser update prevented launch. Please try again.")
            sys.exit(1)

        for driver, manager in WEBDRIVER_MANAGERS.items():
            if driver in str(e).lower():
                options["executable_path"] = manager().install()
                try:
                    return splinter.Browser(name, **options)
                except OSError as e:
                    if driver == "geckodriver" and "arm" in platform.machine():
                        log.error("Your machine's architecture is not supported")
                        log.info(
                            "https://firefox-source-docs.mozilla.org/testing/geckodriver/ARM.html"
                        )
                        sys.exit(1)
                    raise e from None

        raise e from None


LAUNCHERS = {
    "playwright": launch_playwright_browser,
    "splinter": launch_splinter_browser,
}
if playwright is None:
    del LAUNCHERS["playwright"]


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
        page = browser.contexts[0].pages[0]
        # TODO: Figure out how to get the window size instead
        size: dict = page.viewport_size  # type: ignore
    else:
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
