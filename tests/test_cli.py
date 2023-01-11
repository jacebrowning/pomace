# pylint: disable=unused-variable,redefined-outer-name,expression-not-assigned

import platform
from pathlib import Path

import log
import pytest
from cleo.testers.command_tester import CommandTester

from pomace.cli import application
from pomace.models import domain


def describe_alias():
    @pytest.fixture
    def command():
        return CommandTester(application.find("alias"))

    def it_updates_mapping(expect, command):
        command.execute("staging.twitter.com twitter.com")
        log.info(command.io.fetch_output())
        expect(domain("https://staging.twitter.com")) == "twitter.com"


def describe_clean():
    @pytest.fixture
    def command():
        return CommandTester(application.find("clean"))

    def with_domain(command):
        command.execute("twitter.fake")
        log.info(command.io.fetch_output())


def describe_clone():
    @pytest.fixture
    def command():
        return CommandTester(application.find("clone"))

    @pytest.fixture
    def sites():
        # TODO: Get tests passing on AppVeyor CI
        if platform.system() == "Windows":
            pytest.xfail("Git not working on Windows")

        path = Path(__file__).parent / "sites"
        if path.is_dir():
            return path
        return Path(__file__).parent.parent / "sites"

    def with_url(expect, command, sites):
        command.execute("https://github.com/jacebrowning/pomace-twitter.com")
        log.info(command.io.fetch_output())
        path = sites / "twitter.com"
        expect(list((sites).iterdir())).contains(path)

    def with_url_and_domain(expect, command, sites):
        command.execute(
            "https://github.com/jacebrowning/pomace-twitter.com twitter.fake --force"
        )
        log.info(command.io.fetch_output())
        path = sites / "twitter.fake"
        expect(list((sites).iterdir())).contains(path)
