# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

import pytest

from ..types import URL


@pytest.fixture
def url():
    return URL('http://www.example.com/foo/bar')


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
