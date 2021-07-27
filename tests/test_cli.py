# pylint: disable=unused-variable,redefined-outer-name

from pathlib import Path

import pytest
from cleo import ApplicationTester

from pomace.cli import application
from pomace.models import domain


@pytest.fixture
def cli():
    return ApplicationTester(application).execute


def describe_alias():
    def it_updates_mapping(cli):
        cli("alias staging.twitter.com twitter.com")
        assert domain("https://staging.twitter.com") == "twitter.com"


def describe_clean():
    def with_domain(cli):
        cli("clean twitter.fake")


def describe_clone():
    @pytest.fixture
    def root():
        return Path(__file__).parent.parent

    def with_url(cli, root):
        cli("clone https://github.com/jacebrowning/pomace-twitter.com")
        path = root / "sites" / "twitter.com"
        assert path.is_dir(), f"Expected directory: {path}"

    def with_url_and_domain(cli, root):
        cli(
            "clone https://github.com/jacebrowning/pomace-twitter.com"
            " twitter.fake --force"
        )
        path = root / "sites" / "twitter.fake"
        assert path.is_dir(), f"Expected directory: {path}"
