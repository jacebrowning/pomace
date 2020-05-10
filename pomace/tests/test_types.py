# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

import pytest

from ..types import URL


@pytest.fixture
def url():
    return URL('http://www.example.com/foo/bar')


def describe_url():
    def describe_init():
        def with_url(expect, url):
            expect(url.value) == 'http://www.example.com/foo/bar'

        def with_url_and_trailing_slash(expect):
            url = URL('http://example.com/login/error/')
            expect(url.value) == 'http://example.com/login/error'

        def with_path(expect):
            url = URL('example.com', 'login')
            expect(url.value) == 'https://example.com/login'

        def with_path_at_root(expect):
            url = URL('example.com', '@')
            expect(url.value) == 'https://example.com'

        def with_path_and_extra_slashes(expect):
            url = URL('example.com', '/login/error/')
            expect(url.value) == 'https://example.com/login/error'

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

    def describe_path():
        def when_root(expect, url):
            url = URL('http://example.com')
            expect(url.path) == '@'

        def when_single(expect, url):
            url = URL('http://example.com/login')
            expect(url.path) == 'login'

        def when_trailing_slash(expect, url):
            url = URL('http://example.com/login/error/')
            expect(url.path) == 'login/error'

    def describe_fragment():
        def when_default(expect, url):
            expect(url.fragment) == ''

        def when_provided(expect, url):
            url = URL('http://example.com/signup/#step1')
            expect(url.fragment) == 'step1'

        def when_containing_slashes(expect, url):
            url = URL('http://example.com/signup/#/step/2/')
            expect(url.fragment) == 'step_2'
