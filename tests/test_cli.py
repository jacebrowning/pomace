# pylint: disable=unused-variable,redefined-outer-name

from pathlib import Path

import pytest
from cleo import ApplicationTester

from pomace.cli import application


@pytest.fixture
def cli():
    return ApplicationTester(application).execute


def describe_clone():
    def with_url(cli):
        cli("clone https://github.com/jacebrowning/pomace-twitter.com")
        assert Path("sites", "twitter.com").is_dir()

    def with_url_and_domain(cli):
        cli(
            "clone https://github.com/jacebrowning/pomace-twitter.com"
            " twitter.fake --force"
        )
        assert Path("sites", "twitter.fake").is_dir()


def describe_clean():
    def with_domain(cli):
        cli("clean twitter.fake")
