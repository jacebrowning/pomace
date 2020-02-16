# pylint: disable=unused-import

import atexit as _atexit

from pomelo import cli as _cli
from pomelo.settings import settings as _settings


if __name__ == '__main__':
    _atexit.register(_cli.quit_browser)
    print(_settings.label)
    _cli.start_browser()

    from pomelo.shared import browser
    from pomelo import Page, autopage

    page = autopage()
