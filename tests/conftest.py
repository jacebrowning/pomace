"""Integration tests configuration file."""

# pylint: disable=unused-argument,redefined-outer-name

import datafiles
import log
import pytest

from pomace.config import settings


def pytest_configure(config):
    log.init(debug=True)
    log.silence('parse', 'selenium', 'urllib3', allow_info=True)

    terminal = config.pluginmanager.getplugin('terminal')
    terminal.TerminalReporter.showfspath = False


def pytest_runtest_setup(item):
    datafiles.settings.HOOKS_ENABLED = True


@pytest.fixture(scope='session', autouse=True)
def backup_settings():
    backup = settings.datafile.text
    yield
    settings.datafile.text = backup
