# pylint: disable=unused-variable,redefined-outer-name,expression-not-assigned

from pathlib import Path

import log
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
    def root():
        return Path(__file__).parent.parent

    def with_url(expect, cli, root):
        cli("clone https://github.com/jacebrowning/pomace-twitter.com")
        path = root / "sites" / "twitter.com"
        log.info(f"Text path: {path}")
        expect(path.is_dir()) == True

    def with_url_and_domain(expect, cli, root):
        cli(
            "clone https://github.com/jacebrowning/pomace-twitter.com"
            " twitter.fake --force"
        )
        path = root / "sites" / "twitter.fake"
        log.info(f"Text path: {path}")
        expect(path.is_dir()) == True
