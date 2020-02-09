import atexit as _atexit

import log as _log

from pomelo import cli as _cli


if __name__ == '__main__':
    _log.init()
    _log.silence('datafiles')
    _atexit.register(_cli.quit_browser)
    _cli.start_browser()
