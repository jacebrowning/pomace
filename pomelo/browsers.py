import os
import sys

import log
from splinter import Browser
from splinter.exceptions import DriverNotFoundError
from webdriver_manager import chrome, firefox


NAMES = ['Firefox', 'Chrome']

WEBDRIVER_MANAGERS = {
    "chromedriver": chrome.ChromeDriverManager,
    "geckodriver": firefox.GeckoDriverManager,
}


def get(name: str = "", headless: bool = False) -> Browser:
    name = (name or os.getenv("BROWSER") or "").lower()
    options = {"headless": headless, "wait_time": 1.0}

    try:
        return Browser(name, **options) if name else Browser(**options)
    except DriverNotFoundError:
        sys.exit(f"Unsupported browser: {name}")
    except Exception as e:  # pylint: disable=broad-except
        log.debug(str(e))

        for driver, manager in WEBDRIVER_MANAGERS.items():
            if driver in str(e):
                options["executable_path"] = manager().install()
                return Browser(name, **options) if name else Browser(**options)

        raise e from None
