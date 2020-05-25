"""Integration tests configuration file."""

# pylint: disable=unused-argument,redefined-outer-name

import datafiles
import log
import pytest

from pomace import shared, utils
from pomace.config import settings as _settings


def pytest_configure(config):
    log.init(debug=True)
    log.silence('parse', 'selenium', 'urllib3', allow_info=True)

    terminal = config.pluginmanager.getplugin('terminal')
    terminal.TerminalReporter.showfspath = False


def pytest_runtest_setup(item):
    datafiles.settings.HOOKS_ENABLED = True


@pytest.fixture(scope='session', autouse=True)
def settings():
    backup = _settings.datafile.text
    yield _settings
    _settings.datafile.text = backup


@pytest.fixture
def browser(settings):
    settings.browser.name = 'chrome'
    settings.browser.headless = True
    utils.launch_browser()
    return shared.browser
