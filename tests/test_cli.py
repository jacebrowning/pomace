# pylint: disable=unused-variable,redefined-outer-name,expression-not-assigned

from pathlib import Path

import pytest
from cleo import ApplicationTester

from pomace.cli import application
from pomace.models import domain


@pytest.fixture
def cli():
    return ApplicationTester(application).execute


def describe_alias():
    def it_updates_mapping(expect, cli):
        cli("alias staging.twitter.com twitter.com")
        expect(domain("https://staging.twitter.com")) == "twitter.com"


def describe_clean():
    def with_domain(cli):
        cli("clean twitter.fake")


def describe_clone():
    @pytest.fixture
    def sites():
        for path in [
            Path(__file__).parent / "sites",
            Path(__file__).parent.parent / "sites",
        ]:
            if path.is_dir():
                return path
        raise RuntimeError("No sites directory")

    def with_url(expect, cli, sites):
        cli("clone https://github.com/jacebrowning/pomace-twitter.com")
        path = sites / "twitter.com"
        expect(list((sites).iterdir())).contains(path)

    def with_url_and_domain(expect, cli, sites):
        cli(
            "clone https://github.com/jacebrowning/pomace-twitter.com"
            " twitter.fake --force"
        )
        path = sites / "twitter.fake"
        expect(list((sites).iterdir())).contains(path)
