# pylint: disable=unused-argument,expression-not-assigned

import os
from contextlib import suppress

import pytest

from pomace import shared
from pomace.models import Page


def test_locator_uses_are_persisted(expect, browser):
    page = Page.at("https://www.wikipedia.org")
    page.actions = []
    page.datafile.save()
    page.fill_search("foobar")

    page = Page.at("https://www.wikipedia.org")
    locators = sorted(page.fill_search.locators)  # type: ignore
    good_locator = locators[-1]
    bad_locator = locators[0]

    expect(good_locator.uses) > 0
    expect(bad_locator.uses) <= 0


@pytest.mark.xfail(
    "CI" in os.environ, raises=AssertionError, reason="Wikipedia is blocked on CI"
)
def test_type_actions_are_supported(expect, browser):
    page = Page.at("https://www.wikipedia.org")

    page.fill_search("foobar")
    page.type_enter()

    expect(shared.client.url).endswith("wikipedia.org/wiki/Foobar")


@pytest.mark.xfail(
    "CI" in os.environ, raises=AssertionError, reason="Wikipedia is blocked on CI"
)
def test_modifier_keys_are_supported(expect, browser):
    page = Page.at("https://www.wikipedia.org")

    page.fill_search("foobar")
    page.type_tab()
    page.type_shift_tab()
    page.type_enter()

    expect(shared.client.url).endswith("wikipedia.org/wiki/Foobar")


def test_unused_actions_are_removed_on_forced_cleanup(expect, browser):
    page = Page.at("https://www.wikipedia.org")

    page.click_foobar()
    previous_count = len(page.actions)

    page.clean(force=True)
    expect(len(page.actions)) < previous_count


@pytest.mark.xfail(reason="https://github.com/citizenlabsgr/elections-api/issues/357")
def test_links_are_opened_in_the_same_window(expect, browser):
    page = Page.at("https://share.michiganelections.io/elections/41/precincts/1209/")
    with suppress(AttributeError):
        page.click_official_ballot.locators = []
        page.datafile.save()

    page = page.click_official_ballot()

    expect(page.url) == "https://mvic.sos.state.mi.us/Voter/GetMvicBallot/1828/683/"
