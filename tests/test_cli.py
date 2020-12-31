# pylint: disable=unused-variable,redefined-outer-name

import pytest
from cleo import ApplicationTester

from pomace.cli import application


@pytest.fixture
def cli():
    return ApplicationTester(application).execute


def describe_clone():
    def with_url(cli):
        cli("clone https://github.com/jacebrowning/pomace-twitter.com")

    def with_url_and_domain(cli):
        cli("clone https://github.com/jacebrowning/pomace-twitter.com twitter.com")
