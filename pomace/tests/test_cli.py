# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

import pytest

from pomace import cli, config


@pytest.fixture
def mockci(monkeypatch):
    monkeypatch.setenv('CI', 'true')


def describe_prompt_for_browser_if_unset():
    def when_ci(expect, mockci):
        config.settings.browser.name = ''
        cli.prompt_for_browser_if_unset()
        expect(config.settings.browser.name) == 'firefox'


def describe_prompt_for_url_if_unset():
    def when_ci(expect, mockci, mockbrowser):
        config.settings.url = ''
        cli.prompt_for_url_if_unset()
        expect(config.settings.url) == 'http://example.com'


def describe_prompt_for_secret_if_unset():
    def when_ci(expect, mockci, mockbrowser):
        cli.prompt_for_secret_if_unset('foobar')
        expect(config.settings.get_secret('foobar')) == '<unset>'
