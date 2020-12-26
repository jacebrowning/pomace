# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

import pytest

from .. import config, utils


def describe_fake():
    @pytest.fixture(scope="session")
    def fake():
        return utils.Fake()

    def it_includes_zip_code(expect, fake):
        print(repr(fake.zip_code))
        expect(fake.zip_code).isinstance(str)

    def describe_person():
        def it_includes_name_in_email(expect, fake):
            person = fake.person
            expect(person.email).icontains(person.last_name)

        def it_includes_honorific(expect, fake):
            expect(fake.person.honorific).isinstance(str)

        def it_includes_county(expect, fake):
            expect(fake.person.county).isinstance(str)


def describe_prompt_for_browser_if_unset():
    def when_ci(expect, monkeypatch):
        monkeypatch.setenv("CI", "true")
        config.settings.browser.name = ""
        utils.prompt_for_browser_if_unset()
        expect(config.settings.browser.name) == "firefox"

    def when_ci_and_override(expect, monkeypatch):
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("BROWSER", "chrome")
        config.settings.browser.name = ""
        utils.prompt_for_browser_if_unset()
        expect(config.settings.browser.name) == "chrome"


def describe_prompt_for_url_if_unset():
    def when_ci(expect, monkeypatch, mockbrowser):
        monkeypatch.setenv("CI", "true")
        config.settings.url = ""
        utils.prompt_for_url_if_unset()
        expect(config.settings.url) == "http://example.com"


def describe_prompt_for_secret_if_unset():
    def when_ci(expect, monkeypatch, mockbrowser):
        monkeypatch.setenv("CI", "true")
        utils.prompt_for_secret_if_unset("foobar")
        expect(config.settings.get_secret("foobar")) == "<unset>"
