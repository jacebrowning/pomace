# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

from .. import config, prompts


def describe_browser_if_unset():
    def when_ci(expect, monkeypatch):
        monkeypatch.setenv("CI", "true")
        config.settings.browser.name = ""
        prompts.browser_if_unset()
        expect(config.settings.browser.name) == "firefox"

    def when_ci_and_override(expect, monkeypatch):
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("BROWSER", "chrome")
        config.settings.browser.name = ""
        prompts.browser_if_unset()
        expect(config.settings.browser.name) == "chrome"


def describe_url_if_unset():
    def when_ci(expect, monkeypatch, mockbrowser):
        monkeypatch.setenv("CI", "true")
        config.settings.url = ""
        prompts.url_if_unset()
        expect(config.settings.url) == "http://example.com"


def describe_secret_if_unset():
    def when_ci(expect, monkeypatch, mockbrowser):
        monkeypatch.setenv("CI", "true")
        prompts.secret_if_unset("foobar")
        expect(config.settings.get_secret("foobar")) == "<unset>"
