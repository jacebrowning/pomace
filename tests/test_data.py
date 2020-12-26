# pylint: disable=unused-argument,expression-not-assigned

from pomace.models import Page


def test_locator_uses_are_persisted(expect, browser):
    page = Page.at("https://www.wikipedia.org")
    page.actions = []
    page.fill_search("foobar")

    page = Page.at("https://www.wikipedia.org")
    locators = sorted(page.fill_search.locators)
    good_locator = locators[-1]
    bad_locator = locators[0]

    expect(good_locator.uses) > 0
    expect(bad_locator.uses) <= 0


def test_unused_actions_are_removed_on_forced_cleanup(expect, browser):
    page = Page.at("https://www.wikipedia.org")
    page.click_foobar()
    previous_count = len(page.actions)

    page.clean(force=True)
    expect(len(page.actions)) < previous_count
