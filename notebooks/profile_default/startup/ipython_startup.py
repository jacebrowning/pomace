# pylint: disable=unused-import,import-outside-toplevel

import atexit as _atexit

from pomace import Page, autopage, cli as _cli, utils as _utils
from pomace.config import settings
from pomace.shared import browser


def _display_settings():
    from pomace.config import settings

    settings.development_mode_enabled = True

    line = ""
    if settings.browser.name:
        line += settings.browser.name.capitalize()
        if settings.browser.headless:
            line += " (headless)"
    if line and settings.url:
        line += f" -- {settings.url}"

    if line:
        print(line)


def _configure_logging():
    import log

    log.reset()
    log.init(debug=True)
    log.silence('datafiles')


if __name__ == '__main__':
    _atexit.register(_utils.quit_browser)
    _display_settings()
    _cli.RunCommand().launch_browser()

    page = autopage()

    _configure_logging()
