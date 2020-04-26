import time

from . import browser, shared
from .config import settings


def launch_browser(delay: float = 0.0):
    if not shared.browser:
        shared.browser = browser.launch()
    browser.resize(shared.browser)
    shared.browser.visit(settings.url)
    time.sleep(delay)


def quit_browser():
    if shared.browser:
        browser.save_size(shared.browser)
        shared.browser.quit()
