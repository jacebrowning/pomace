# pylint: disable=unused-import,import-outside-toplevel


import pomace
from pomace import prompts as _prompts
from pomace import utils as _utils
from pomace.config import settings
from pomace.models import Page, auto
from pomace.shared import browser


def _configure_logging():
    import log

    log.reset()
    log.init(debug=True)
    log.silence("datafiles")


def _display_settings():
    from pomace.config import settings

    line = ""
    if settings.browser.name:
        line += settings.browser.name.capitalize()
        if settings.browser.headless:
            line += " (headless)"
    if line and settings.url:
        line += f" -- {settings.url}"

    if line:
        print(line)
        _prompts.linebreak(force=True)


if __name__ == "__main__":
    _configure_logging()
    _display_settings()
    _prompts.browser_if_unset()
    _prompts.url_if_unset()
    _utils.launch_browser()

    page = auto()
