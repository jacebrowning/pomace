# pylint: disable=expression-not-assigned,unused-variable,redefined-outer-name,unused-argument

import pytest
import requests

from ..models import Action, Locator, Page


@pytest.fixture
def locator():
    return Locator("name", "email")


@pytest.fixture
def action():
    return Action("fill", "email")


@pytest.fixture
def page(mockbrowser):
    return Page("example.com", "/foo/bar")


def describe_locator():
    def describe_bool():
        def it_is_false_when_placeholder(expect, locator):
            expect(bool(locator)) == True
            locator.value = ""
            expect(bool(locator)) == False

    def describe_sort():
        def it_orders_by_uses(expect):
            locators = [
                Locator("name", "bbb", uses=5),
                Locator("name", "aaa", uses=6),
                Locator("name", "BBB", uses=6),
                Locator("name", "AAA", uses=7),
                Locator("name", "zzz", uses=8),
            ]
            expect(sorted(locators)) == locators

    def describe_find():
        def it_returns_callable(expect, mockbrowser, locator):
            expect(locator.find()) == "mockelement:name=email"

        def it_can_find_links_by_partial_text(expect, mockbrowser, locator):
            locator.mode = "text (partial)"
            expect(locator.find()) == "mockelement:links.partial_text=email"

        def it_can_find_links_by_aria_label(expect, mockbrowser, locator):
            locator.mode = "aria-label"
            expect(locator.find()) == 'mockelement:css=[aria-label="email"]'

    def describe_score():
        def it_updates_uses(expect, locator):
            expect(locator.score(+1)) == True
            expect(locator.uses) == 1

        def it_tops_out_at_max_value(expect, locator):
            locator.score(+99)
            expect(locator.score(+1)) == False
            expect(locator.uses) == 99

        def it_bottoms_out_at_min_value(expect, locator):
            locator.score(-1)
            expect(locator.score(-1)) == False
            expect(locator.uses) == -1


def describe_action():
    def describe_str():
        def it_includes_the_verb_and_name(expect, action):
            expect(str(action)) == "fill_email"

    def describe_humanized():
        def it_describes_the_action(expect, action):
            expect(action.humanized) == "Filling email"

    def describe_sorted_locators():
        def it_orders_by_use(expect, action):
            action.locators = [
                Locator("id", "email", uses=-2),
                Locator("name", "email", uses=-3),
                Locator("value", "email", uses=-1),
            ]
            modes = [locator.mode for locator in action.sorted_locators]
            expect(modes) == ["value", "id", "name"]

        def it_tries_new_locators_first(expect, action):
            action.locators = [
                Locator("name", "email", uses=-1),
                Locator("id", "email", uses=0),
            ]
            expect(len(action.sorted_locators)) == 1
            expect(action.locator.mode) == "id"

        def it_only_includes_invalid_locators_when_no_other_options(expect, action):
            action.locators = [
                Locator("id", "email", uses=2),
                Locator("name", "email", uses=3),
                Locator("value", "email", uses=-1),
            ]
            modes = [locator.mode for locator in action.sorted_locators]
            expect(modes) == ["name", "id"]

    def describe_locator():
        def it_returns_placeholder_when_no_locators_defined(expect, action):
            action.locators = []
            expect(action.locator.value) == "placeholder"

    def describe_bool():
        def it_is_false_when_placeholder(expect, action):
            expect(bool(action)) == True
            action.name = ""
            expect(bool(action)) == False

    def describe_clean():
        def it_removes_unused_locators(expect, action):
            previous_count = len(action.locators)
            action.locators[0].uses = -1
            action.locators[1].uses = 99

            expect(action.clean("<page>")) == previous_count - 1
            expect(len(action.locators)) == 1

        def it_requires_one_locator_to_exceed_usage_threshold(expect, action):
            previous_count = len(action.locators)
            action.locators[0].uses = 98

            expect(action.clean("<page>")) == 0
            expect(len(action.locators)) == previous_count

        def it_can_be_forced(expect, action):
            previous_count = len(action.locators)
            action.locators[0].uses = 1

            expect(action.clean("<page>", force=True)) == previous_count - 1
            expect(len(action.locators)) == 1

        def it_keeps_used_locators(expect, action):
            action.locators = [Locator("mode", "value", uses=1)]

            expect(action.clean("<page>", force=True)) == 0
            expect(len(action.locators)) == 1


def describe_page():
    def describe_repr():
        def it_includes_the_url(expect, page):
            expect(repr(page)) == "Page.at('https://example.com/foo/bar')"

        def it_includes_the_variant_when_set(expect, page):
            page.variant = "qux"
            expect(
                repr(page)
            ) == "Page.at('https://example.com/foo/bar', variant='qux')"

    def describe_str():
        def it_returns_the_url(expect, page):
            expect(str(page)) == "https://example.com/foo/bar"

        def it_includes_the_variant_when_set(expect, page):
            page.variant = "qux"
            expect(str(page)) == "https://example.com/foo/bar (qux)"

    def describe_dir():
        def it_lists_valid_actions(expect, page, action):
            page.actions = []
            expect(dir(page)) == []
            page.actions.append(action)
            expect(dir(page)) == ["fill_email"]

    def describe_getattr():
        def it_returns_matching_action(expect, page, action):
            page.actions = [action]
            expect(getattr(page, "fill_email")) == action

        def it_adds_missing_actions(expect, page, monkeypatch):
            page.actions = []
            new_action = getattr(page, "fill_password")
            expect(new_action.verb) == "fill"
            expect(new_action.name) == "password"
            expect(len(new_action.locators)) > 1

        def it_rejects_invalid_actions(expect, page):
            with expect.raises(AttributeError):
                getattr(page, "mash_password")

        def it_rejects_missing_attributes(expect, page):
            with expect.raises(AttributeError):
                getattr(page, "foobar")

    def describe_contains():
        def it_matches_partial_html(expect, page, mockbrowser):
            expect(page).contains("world")

    def describe_clean():
        def it_removes_unused_locators(expect, page):
            page.locators.inclusions = [
                Locator("id", "foo", uses=0),
                Locator("id", "bar", uses=-1),
                Locator("id", "qux", uses=99),
            ]
            page.locators.exclusions = [
                Locator("id", "foo", uses=0),
                Locator("id", "bar", uses=-1),
                Locator("id", "qux", uses=99),
            ]

            expect(page.clean()) == 4
            expect(len(page.locators.inclusions)) == 1
            expect(len(page.locators.exclusions)) == 1

    def describe_properties():
        @pytest.mark.vcr()
        def it_computes_values_based_on_the_html(expect, page, mockbrowser):
            mockbrowser.html = requests.get("http://example.com").text
            expect(page.text) == (
                "Example Domain\n"
                "Example Domain\n"
                "This domain is for use in illustrative examples in documents. You may use this\n"
                "domain in literature without prior coordination or asking for permission.\n"
                "More information..."
            )
            expect(page.identity) == 19078
