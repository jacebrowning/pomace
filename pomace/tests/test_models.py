# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

import pytest

from ..models import Action, Locator, Page


@pytest.fixture
def locator():
    return Locator('name', 'email')


@pytest.fixture
def action():
    return Action('fill', 'email')


@pytest.fixture
def page():
    return Page('example.com', '/foo/bar')


def describe_locator():
    def describe_bool():
        def it_is_false_when_placeholder(expect, locator):
            expect(bool(locator)) == True
            locator.value = ''
            expect(bool(locator)) == False

    def describe_sort():
        def it_orders_by_score(expect):
            locators = [
                Locator('name', 'bbb', score=0.5),
                Locator('name', 'aaa', score=0.6),
                Locator('name', 'BBB', score=0.6),
                Locator('name', 'AAA', score=0.7),
                Locator('name', 'zzz', score=0.8),
            ]
            expect(sorted(locators)) == locators

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

        def it_adds_missing_actions(expect, page, monkeypatch):
            page.actions = []
            new_action = getattr(page, 'fill_password')
            expect(new_action.verb) == 'fill'
            expect(new_action.name) == 'password'
            expect(len(new_action.locators)) > 1

        def it_rejects_invalid_actions(expect, page):
            with expect.raises(AttributeError):
                getattr(page, 'mash_password')

        def it_rejects_missing_attributes(expect, page):
            with expect.raises(AttributeError):
                getattr(page, 'foobar')

    def describe_contains():
        def it_matches_partial_html(expect, page, mockbrowser):
            expect(page).contains("world")
