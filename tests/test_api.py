# pylint: disable=unused-variable,expression-not-assigned

import os
from pathlib import Path

import pytest

import pomace
from pomace.config import settings


def test_package_contents(expect):
    names = [name for name in dir(pomace) if not name.startswith("_")]
    expect(names).contains("auto")
    expect(names).contains("Page")
    expect(names).contains("visit")
    expect(names).excludes("get_distribution")


def describe_visit():
    @pytest.mark.xfail(
        os.name == "nt", reason="WebDriver Manager is not working on Windows"
    )
    def it_launches_a_browser(expect):
        page = pomace.visit("http://example.com", browser="chrome", headless=True)
        expect(page).contains("Example Domain")

    @pytest.mark.xfail(os.name == "nt", reason="Path differs on Windows")
    def it_saves_data_relative_to_caller(expect):
        page = pomace.visit("http://example.com", browser="chrome", headless=True)
        path = Path(__file__).parent / "sites" / "example.com" / "@" / "default.yml"
        expect(page.datafile.path) == path


def describe_freeze():
    @pytest.mark.xfail(
        os.name == "nt", reason="WebDriver Manager is not working on Windows"
    )
    def it_disables_automatic_actions(expect):
        page = pomace.visit("http://example.com", browser="chrome", headless=True)
        page.actions = []
        page.datafile.save()

        pomace.freeze()
        try:
            page.click_foobar()
            expect(dir(page)).excludes("click_foobar")
        finally:
            settings.dev = True
