# pylint: disable=unused-argument,expression-not-assigned

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
    if hasattr(page, "click_gruul_adventures"):
        page.click_gruul_adventures.locators = []
        page.datafile.save()

    page.click_gruul_adventures()

    expect(page.click_gruul_adventures.sorted_locators[0].index) == 1
