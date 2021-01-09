# pylint: disable=no-self-use,unused-argument

"""Unit tests configuration file."""


import datafiles
import log
import pytest

from pomace import shared


class MockElement(str):
    @property
    def outer_html(self):
        return f"<mockhtml>{self}</>"

    @property
    def visible(self):
        return True


class MockLinks:
    def find_by_partial_text(self, value):
        return [MockElement(f"mockelement:links.partial_text={value}")]


class MockBrowser:

    url = "http://example.com"

    html = "Hello, world!"

    def find_by_name(self, value):
        return [MockElement(f"mockelement:name={value}")]

    links = MockLinks()


@pytest.fixture
def mockbrowser(monkeypatch):
    monkeypatch.setattr(shared, "browser", MockBrowser())


def pytest_configure(config):
    log.init(debug=True)
    log.silence("faker")

    terminal = config.pluginmanager.getplugin("terminal")
    terminal.TerminalReporter.showfspath = False


def pytest_runtest_setup(item):
    datafiles.settings.HOOKS_ENABLED = False
