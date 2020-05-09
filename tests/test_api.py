# pylint: disable=unused-variable

import pomace


def describe_visit():
    def it_launches_a_browser(expect):
        page = pomace.visit("http://example.com", browser='chrome', headless=True)
        expect(page).contains("Example Domain")
