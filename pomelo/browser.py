import sys

import log
from splinter import Browser
from splinter.exceptions import DriverNotFoundError
from webdriver_manager import chrome, firefox

from .settings import settings


NAMES = ['Firefox', 'Chrome']

WEBDRIVER_MANAGERS = {
    "chromedriver": chrome.ChromeDriverManager,
    "geckodriver": firefox.GeckoDriverManager,
}


def launch() -> Browser:
    name = settings.browser.name
    options = {"headless": settings.browser.headless, "wait_time": 1.0}

    try:
        return Browser(name, **options)
    except DriverNotFoundError:
        sys.exit(f"Unsupported browser: {settings.browser.name}")
    except Exception as e:  # pylint: disable=broad-except
        log.debug(str(e))

        for driver, manager in WEBDRIVER_MANAGERS.items():
            if driver in str(e):
                options["executable_path"] = manager().install()
                return Browser(name, **options)

        raise e from None


def resize(browser: Browser):
    browser.driver.set_window_size(settings.browser.width, settings.browser.height)
    browser.driver.set_window_position(0, 0)
    size = browser.driver.get_window_size()
    log.debug(f'Resized browser: {size}')


def save_size(browser: Browser):
    size = browser.driver.get_window_size()
    settings.browser.width = size['width']
    settings.browser.height = size['height']
    log.debug(f'Saved new browser size: {size}')
