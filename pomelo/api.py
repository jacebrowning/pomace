# pylint: disable=unused-import,import-outside-toplevel

import atexit

from . import cli, models, shared


def visit(url: str) -> models.Page:
    atexit.register(cli.quit_browser)
    cli.launch_browser()
    shared.browser.visit(url)
    return models.autopage()
