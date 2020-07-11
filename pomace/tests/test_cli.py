# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument


from pomace import cli, config


def describe_prompt_for_browser_if_unset():
    def when_ci(expect, monkeypatch):
        monkeypatch.setenv('CI', 'true')
        config.settings.browser.name = ''
        cli.prompt_for_browser_if_unset()
        expect(config.settings.browser.name) == 'firefox'

    def when_ci_and_override(expect, monkeypatch):
        monkeypatch.setenv('CI', 'true')
        monkeypatch.setenv('BROWSER', 'chrome')
        config.settings.browser.name = ''
        cli.prompt_for_browser_if_unset()
        expect(config.settings.browser.name) == 'chrome'


def describe_prompt_for_url_if_unset():
    def when_ci(expect, monkeypatch, mockbrowser):
        monkeypatch.setenv('CI', 'true')
        config.settings.url = ''
        cli.prompt_for_url_if_unset()
        expect(config.settings.url) == 'http://example.com'


def describe_prompt_for_secret_if_unset():
    def when_ci(expect, monkeypatch, mockbrowser):
        monkeypatch.setenv('CI', 'true')
        cli.prompt_for_secret_if_unset('foobar')
        expect(config.settings.get_secret('foobar')) == '<unset>'
