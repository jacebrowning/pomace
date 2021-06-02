# pylint: disable=unused-argument,expression-not-assigned

from contextlib import suppress

from pomace import shared
from pomace.models import Page


def test_locator_uses_are_persisted(expect, browser):
    page = Page.at("https://www.wikipedia.org")
    page.actions = []
    page.datafile.save()
    page.fill_search("foobar")

    page = Page.at("https://www.wikipedia.org")
    locators = sorted(page.fill_search.locators)
    good_locator = locators[-1]
    bad_locator = locators[0]

    expect(good_locator.uses) > 0
    expect(bad_locator.uses) <= 0


def test_type_actions_are_supported(expect, browser):
    page = Page.at("https://www.wikipedia.org")

    page.fill_search("foobar")
    page.type_enter()

    expect(shared.browser.url) == "https://en.wikipedia.org/wiki/Foobar"


def test_modifier_keys_are_supported(expect, browser):
    page = Page.at("https://www.wikipedia.org")

    page.fill_search("foobar")
    page.type_tab()
    page.type_shift_tab()
    page.type_enter()

    expect(shared.browser.url) == "https://en.wikipedia.org/wiki/Foobar"


def test_unused_actions_are_removed_on_forced_cleanup(expect, browser):
    page = Page.at("https://www.wikipedia.org")

    page.click_foobar()
    previous_count = len(page.actions)

    page.clean(force=True)
    expect(len(page.actions)) < previous_count


def test_multiple_indices_are_tried(expect, browser):
    page = Page.at("https://www.mtggoldfish.com/metagame/standard#paper")
    with suppress(AttributeError):
        page.click_sultai_control.locators = []
        page.datafile.save()

    page.click_sultai_control()

    expect(page.click_sultai_control.sorted_locators[0].index) == 1


def test_links_are_opened_in_the_same_window(expect, browser):
    page = Page.at("https://share.michiganelections.io/elections/41/precincts/1209/")
    with suppress(AttributeError):
        page.click_official_ballot.locators = []
        page.datafile.save()

    page = page.click_official_ballot()

    expect(page.url) == "https://mvic.sos.state.mi.us/Voter/GetMvicBallot/1828/683/"
