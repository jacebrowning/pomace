# pylint: disable=no-self-use

import os
from importlib import import_module, reload

import log
from cleo import Application, Command
from IPython import embed

from . import models, shared, utils
from .config import settings


class BaseCommand(Command):
    def handle(self):
        log.reset()
        log.init(verbosity=self.io.verbosity + 1)
        log.silence("datafiles", allow_warning=True)
        self.update_settings()
        utils.prompt_for_browser_if_unset()
        utils.prompt_for_url_if_unset()
        utils.launch_browser()
        utils.locate_models()
        try:
            self.run_loop()
        finally:
            utils.quit_browser()
            print()

    def update_settings(self):
        if self.option("root"):
            os.chdir(self.option("root"))

        if self.option("browser"):
            settings.browser.name = self.option("browser").lower()

        settings.browser.headless = self.option("headless")

        if self.option("domain"):
            settings.url = "https://" + self.option("domain")


class ShellCommand(BaseCommand):
    """
    Launch an interactive shell

    shell
        {--browser= : Browser to use for automation}
        {--headless : Run the specified browser in a headless mode}
        {--domain= : Starting domain for the automation}
        {--root= : Directory to load models from}
    """

    def run_loop(self):
        # pylint: disable=unused-variable
        pomace = import_module("pomace")
        Page = models.Page
        autopage = models.autopage
        page = autopage()
        embed(colors="neutral")


class RunCommand(BaseCommand):
    """
    Run pomace in a loop

    run
        {--browser= : Browser to use for automation}
        {--headless : Run the specified browser in a headless mode}
        {--domain= : Starting domain for the automation}
        {--root= : Directory to load models from}
    """

    RELOAD_ACTIONS = "<reload actions>"

    def run_loop(self):
        self.clear_screen()
        page = models.autopage()
        self.display_url(page)
        while True:
            choices = [self.RELOAD_ACTIONS] + dir(page)
            command = shared.cli.Bullet(
                prompt="\nSelect an action: ", bullet=" ● ", choices=choices
            )
            action = command.launch()
            if action == self.RELOAD_ACTIONS:
                reload(models)
                self.clear_screen()
                page = models.autopage()
                self.display_url(page)
                continue

            command = shared.cli.Input(prompt="\nValue: ")
            page, transitioned = page.perform(action, prompt=command.launch)
            if transitioned:
                self.clear_screen()
                self.display_url(page)

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def display_url(self, page):
        self.line(f"<fg=white;options=bold>{page}</>")


application = Application()
application.add(ShellCommand())
application.add(RunCommand())
