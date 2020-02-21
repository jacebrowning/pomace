from . import browser, shared
from .config import settings


def launch_browser():
    shared.browser = browser.launch()
    browser.resize(shared.browser)
    shared.browser.visit(settings.site.url)


def quit_browser():
    if shared.browser:
        browser.save_size(shared.browser)
        shared.browser.quit()
