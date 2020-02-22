# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

import pytest

from ..models import URL, Action, Locator, Page


@pytest.fixture
def url():
    return URL('http://www.example.com/foo/bar')


@pytest.fixture
def locator():
    return Locator('name', 'email')


@pytest.fixture
def action():
    return Action('fill', 'email')


@pytest.fixture
def page():
    return Page('example.com', '/foo/bar')


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

        def it_matches_patterns(expect):
            pattern = URL('http://example.com/p/{name}')
            expect(pattern) == URL('http://example.com/p/foobar')
            expect(pattern) != URL('http://example.com/')
            expect(pattern) != URL('http://example.com/p/foo/bar')

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


def describe_page():
    def describe_repr():
        def it_includes_the_url(expect, page):
            expect(repr(page)) == "Page.at('https://example.com/foo/bar')"

        def it_includes_the_variant_when_set(expect, page):
            page.variant = 'qux'
            expect(
                repr(page)
            ) == "Page.at('https://example.com/foo/bar', variant='qux')"

    def describe_str():
        def it_returns_the_url(expect, page):
            expect(str(page)) == 'https://example.com/foo/bar'

        def it_includes_the_variant_when_set(expect, page):
            page.variant = 'qux'
            expect(str(page)) == 'https://example.com/foo/bar (qux)'

    def describe_dir():
        def it_lists_valid_actions(expect, page, action):
            page.actions = []
            expect(dir(page)) == []
            page.actions.append(action)
            expect(dir(page)) == ['fill_email']

    def describe_getattr():
        def it_returns_matching_action(expect, page, action):
            page.actions = [action]
            expect(getattr(page, 'fill_email')) == action

        def it_adds_missing_actions(expect, page):
            page.actions = []
            new_action = getattr(page, 'fill_password')
            expect(new_action.verb) == 'fill'
            expect(new_action.name) == 'password'

        def it_rejects_invalid_actions(expect, page):
            with expect.raises(AttributeError):
                getattr(page, 'mash_password')

        def it_rejects_missing_attributes(expect, page):
            with expect.raises(AttributeError):
                getattr(page, 'foobar')
