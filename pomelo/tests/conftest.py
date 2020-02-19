# pylint: disable=no-self-use

"""Unit tests configuration file."""


import log
import pytest

from pomelo import shared


class MockLinks:
    def find_by_partial_text(self, value):
        return f'<mockelement: links.partial_text={value}>'


class MockBrowser:
    def find_by_name(self, value):
        return f'<mockelement: name={value}>'

    links = MockLinks()


@pytest.fixture
def mockbrowser(monkeypatch):
    monkeypatch.setattr(shared, 'browser', MockBrowser())


def pytest_configure(config):
    """Disable verbose output when running tests."""
    log.init(debug=True)

    terminal = config.pluginmanager.getplugin('terminal')
    terminal.TerminalReporter.showfspath = False
