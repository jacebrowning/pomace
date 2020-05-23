import time

import log

from . import browser, shared
from .config import settings


def launch_browser(delay: float = 0.0) -> bool:
    launched = False
    if not shared.browser:
        shared.browser = browser.launch()
        browser.resize(shared.browser)
        launched = True
    shared.browser.visit(settings.url)
    time.sleep(delay)
    return launched


def quit_browser(silence_logging: bool = False):
    if silence_logging:
        log.silence('pomace', 'selenium', allow_warning=True)
    try:
        browser.save_url(shared.browser)
        browser.save_size(shared.browser)
        shared.browser.quit()
    except Exception as e:
        log.debug(e)
