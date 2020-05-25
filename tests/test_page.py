# pylint: disable=unused-variable,unused-argument,expression-not-assigned

import pomace


def describe_persistence():
    def it_saves_locator_scores(expect):
        page = pomace.visit(
            "https://www.wikipedia.org", browser='chrome', headless=True
        )
        page.actions = []
        page.fill_search("foobar")
        # page.fill_search("foobar")  # second attribute access triggers save

        page = pomace.visit(
            "https://www.wikipedia.org", browser='chrome', headless=True
        )
        locators = sorted(page.fill_search.locators)
        good_locator = locators[-1]
        bad_locator = locators[0]

        expect(good_locator.score) > 0.5
        expect(bad_locator.score) < 0.5
