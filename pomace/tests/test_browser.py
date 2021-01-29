# pylint: disable=unused-variable,expression-not-assigned

from pomace import browser
from pomace.config import settings


def describe_launch():
    def it_requires_a_browser_to_be_set(expect):
        settings.browser.name = ""
        with expect.raises(SystemExit):
            browser.launch()

    def it_rejects_invalid_browsers(expect):
        settings.browser.name = "foobar"
        with expect.raises(SystemExit):
            browser.launch()

    def it_forces_lowercase_browser_name(expect, mocker):
        settings.browser.name = "Firefox"
        mocker.patch.object(browser, "Browser")
        browser.launch()
        expect(settings.browser.name) == "firefox"

    def it_handles_unspecified_browser(expect, mocker):
        settings.browser.name = "open"
        mocker.patch.object(browser, "Browser")
        browser.launch()
        expect(settings.browser.name) == "firefox"
