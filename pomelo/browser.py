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
