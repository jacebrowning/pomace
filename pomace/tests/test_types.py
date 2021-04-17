# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

import log
import pytest

from ..types import URL, Fake


@pytest.fixture
def url():
    return URL("http://www.example.com/foo/bar")


def describe_url():
    def describe_init():
        def with_url(expect, url):
            expect(url.value) == "http://www.example.com/foo/bar"

        def with_url_and_trailing_slash(expect):
            url = URL("http://example.com/login/error/")
            expect(url.value) == "http://example.com/login/error"

        def with_path(expect):
            url = URL("example.com", "login")
            expect(url.value) == "https://example.com/login"

        def with_path_at_root(expect):
            url = URL("example.com", "@")
            expect(url.value) == "https://example.com"

        def with_path_and_extra_slashes(expect):
            url = URL("example.com", "/login/error/")
            expect(url.value) == "https://example.com/login/error"

    def describe_str():
        def it_returns_the_value(expect, url):
            expect(str(url)) == "http://www.example.com/foo/bar"

    def describe_eq():
        def it_compares_domain_and_path(expect, url):
            expect(url) == URL("https://www.example.com/foo/bar/")
            expect(url) != URL("http://example.com/foo/bar")

        def it_matches_patterns(expect):
            pattern = URL("http://example.com/p/{name}")
            expect(pattern) == URL("http://example.com/p/foobar")
            expect(pattern) != URL("http://example.com/")
            expect(pattern) != URL("http://example.com/p")
            expect(pattern) != URL("http://example.com/p/foo/bar")

        def it_does_not_match_root_placeholder(expect):
            pattern = URL("http://example.com/{value}")
            expect(pattern) != URL("http://example.com")

        def it_can_be_compared_to_str(expect, url):
            expect(url) == str(url)
            expect(url) == str(url) + "/"
            expect(url) != str(url) + "_extra"

    def describe_contains():
        def it_checks_url_contents(expect, url):
            expect(url).contains("foo/bar")
            expect(url).excludes("qux")

    def describe_path():
        def when_root(expect, url):
            url = URL("http://example.com")
            expect(url.path) == "@"

        def when_single(expect, url):
            url = URL("http://example.com/login")
            expect(url.path) == "login"

        def when_trailing_slash(expect, url):
            url = URL("http://example.com/login/error/")
            expect(url.path) == "login/error"

    def describe_fragment():
        def when_default(expect, url):
            expect(url.fragment) == ""

        def when_provided(expect, url):
            url = URL("http://example.com/signup/#step1")
            expect(url.fragment) == "step1"

        def when_containing_slashes(expect, url):
            url = URL("http://example.com/signup/#/step/2/")
            expect(url.fragment) == "step_2"


def describe_fake():
    @pytest.fixture
    def fake():
        return Fake()

    @pytest.mark.parametrize(
        "name",
        [
            "email_address",
            "zip_code",
        ],
    )
    def it_maps_aliases(expect, fake, name):
        value = getattr(fake, name)
        expect(value).isinstance(str)

    def it_handles_missing_attributes(expect, fake):
        with expect.raises(AttributeError):
            getattr(fake, "foobar")


def describe_person():
    @pytest.fixture
    def person():
        return Fake().person

    def it_includes_email_in_str(expect, person):
        expect(str(person)).contains("<")
        expect(str(person)).contains("@")

    def it_includes_name_in_email(expect, person):
        expect(person.email).icontains(person.last_name)

    def it_includes_state_name_and_abbr(expect, person):
        log.info(f"State: {person.state} ({person.state_abbr})")
        expect(len(person.state)) >= 4
        expect(len(person.state_abbr)) == 2

    @pytest.mark.parametrize(
        "name",
        [
            "address",
            "birthday",
            "cell_phone",
            "county",
            "email",
            "honorific",
            "phone",
            "prefix",
            "street_address",
            "zip",
        ],
    )
    def it_maps_aliases(expect, person, name):
        value = getattr(person, name)
        expect(value).isinstance(str)

    def it_handles_missing_attributes(expect, person):
        with expect.raises(AttributeError):
            getattr(person, "foobar")
