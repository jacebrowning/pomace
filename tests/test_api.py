# pylint: disable=unused-variable,expression-not-assigned

from pathlib import Path

import pomace


def describe_visit():
    def it_launches_a_browser(expect):
        page = pomace.visit("http://example.com", browser='chrome', headless=True)
        expect(page).contains("Example Domain")

    def it_saves_data_relative_to_caller(expect):
        page = pomace.visit("http://example.com", browser='chrome', headless=True)
        path = Path(__file__).parent / 'sites' / 'example.com' / '@' / 'default.yml'
        expect(page.datafile.path) == path.resolve()
