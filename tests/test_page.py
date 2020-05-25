# pylint: disable=unused-variable,unused-argument,expression-not-assigned

from pomace.models import Page


def describe_persistence():
    def it_saves_locator_scores(expect, browser):
        page = Page.at("https://www.wikipedia.org")
        page.actions = []
        page.fill_search("foobar")

        page = Page.at("https://www.wikipedia.org")
        locators = sorted(page.fill_search.locators)
        good_locator = locators[-1]
        bad_locator = locators[0]

        expect(good_locator.score) > 0.5
        expect(bad_locator.score) < 0.5
