# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

import pytest

from ..models import URL, Action, Locator


@pytest.fixture
def url():
    return URL('http://www.example.com/foo/bar')


@pytest.fixture
def locator():
    return Locator('name', 'email')


@pytest.fixture
def action():
    return Action('fill', 'email')


def describe_url():
    def describe_init():
        def it_removes_escaped_slashes(expect, monkeypatch):
            monkeypatch.setattr(URL, 'SLASH', '@')
            url = URL('www.example.com', '@foo@bar')
            expect(url.domain) == 'www.example.com'
            expect(url.path) == '/foo/bar'

    def describe_str():
        def it_returns_the_value(expect, url):
            expect(str(url)) == 'http://www.example.com/foo/bar'

    def describe_eq():
        def it_compares_domain_and_path(expect, url):
            expect(url) == URL('https://www.example.com/foo/bar/')
            expect(url) != URL('http://example.com/foo/bar')

    def describe_path_encoded():
        def it_replaces_slashes_with_special_character(expect, monkeypatch, url):
            monkeypatch.setattr(URL, 'SLASH', '@')
            expect(url.domain) == 'www.example.com'
            expect(url.path_encoded) == '@foo@bar'


def describe_locator():
    def describe_bool():
        def it_is_false_when_placeholder(expect, locator):
            expect(bool(locator)) == True
            locator.value = ''
            expect(bool(locator)) == False

    def describe_find():
        def it_returns_callable(expect, mockbrowser, locator):
            expect(locator.find()) == '<mockelement: name=email>'

        def it_can_find_links_by_partial_text(expect, mockbrowser, locator):
            locator.mode = 'partial_text'
            expect(locator.find()) == '<mockelement: links.partial_text=email>'


def describe_action():
    def describe_str():
        def it_includes_the_verb_and_name(expect, action):
            expect(str(action)) == 'fill_email'

    def describe_bool():
        def it_is_false_when_placeholder(expect, action):
            expect(bool(action)) == True
            action.name = ''
            expect(bool(action)) == False
