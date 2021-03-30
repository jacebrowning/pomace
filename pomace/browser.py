import sys

import log
from splinter import Browser
from splinter.exceptions import DriverNotFoundError
from webdriver_manager import chrome, firefox

from .config import settings


NAMES = ["Firefox", "Chrome"]

WEBDRIVER_MANAGERS = {
    "chromedriver": chrome.ChromeDriverManager,
    "geckodriver": firefox.GeckoDriverManager,
}


def launch() -> Browser:
    options = {"headless": settings.browser.headless, "wait_time": 1.0}

    if not settings.browser.name:
        sys.exit("No browser specified")

    if settings.browser.name == "open":
        settings.browser.name = NAMES[0]

    settings.browser.name = settings.browser.name.lower()
    log.info(f"Launching browser: {settings.browser.name}")

    try:
        return Browser(settings.browser.name, **options)
    except DriverNotFoundError:
        sys.exit(f"Unsupported browser: {settings.browser.name}")
    except Exception as e:  # pylint: disable=broad-except
        log.debug(str(e))

        if "exited process" in str(e):
            sys.exit("Browser update prevented launch. Please try again.")

        for driver, manager in WEBDRIVER_MANAGERS.items():
            if driver in str(e).lower():
                options["executable_path"] = manager().install()
                return Browser(settings.browser.name, **options)

        raise e from None


def resize(browser: Browser):
    browser.driver.set_window_size(settings.browser.width, settings.browser.height)
    browser.driver.set_window_position(0, 0)
    size = browser.driver.get_window_size()
    log.debug(f"Resized browser: {size}")


def save_url(browser: Browser):
    if settings.browser != browser.url:
        log.debug(f"Saving last browser URL: {browser.url}")
        settings.url = browser.url


def save_size(browser: Browser):
    size = browser.driver.get_window_size()
    if size != (settings.browser.width, settings.browser.height):
        log.debug(f"Saving last browser size: {size}")
        settings.browser.width = size["width"]
        settings.browser.height = size["height"]
