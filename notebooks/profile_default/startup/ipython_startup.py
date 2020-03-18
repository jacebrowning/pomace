# pylint: disable=unused-import,import-outside-toplevel

import atexit as _atexit

from pomace import cli as _cli, utils as _utils


def _display_settings():
    from pomace.config import settings

    settings.development_mode_enabled = True

    line = ""
    if settings.browser.name:
        line += settings.browser.name.capitalize()
        if settings.browser.headless:
            line += " (headless)"
    if line and settings.site.domain:
        line += f" -- {settings.site.url}"

    if line:
        print(line)


if __name__ == '__main__':
    _atexit.register(_utils.quit_browser)
    _display_settings()
    _cli.RunCommand().launch_browser()

    from pomace.shared import browser
    from pomace import Page, autopage
    from pomace.config import settings

    page = autopage()
