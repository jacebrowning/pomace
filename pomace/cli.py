# pylint: disable=no-self-use

import os
from importlib import import_module, reload

import log
from cleo import Application, Command
from IPython import embed

from . import models, prompts, utils
from .config import settings


class BaseCommand(Command):
    def handle(self):
        log.reset()
        log.init(verbosity=self.io.verbosity + 1)
        log.silence("datafiles", allow_warning=True)
        self.update_settings()
        prompts.browser_if_unset()
        domains = list(set(p.domain for p in models.Page.objects.all()))
        prompts.url_if_unset(domains)
        utils.launch_browser()
        utils.locate_models()
        try:
            self.run_loop()
        finally:
            utils.quit_browser()
            prompts.linebreak()

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

    def run_loop(self):
        self.clear_screen()
        page = models.autopage()
        self.display_url(page)
        while True:
            action = prompts.action(page)
            if action is None:
                reload(models)
                self.clear_screen()
                page = models.autopage()
                self.display_url(page)
                continue

            page, transitioned = page.perform(action)
            if transitioned:
                self.clear_screen()
                self.display_url(page)

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def display_url(self, page):
        self.line(f"<fg=white;options=bold>{page}</>")
        prompts.linebreak(force=True)


class CleanCommand(BaseCommand):
    """
    Remove all unused actions and locators

    clean
        {--root= : Directory to load models from}
    """

    def handle(self):
        log.reset()
        log.init(verbosity=self.io.verbosity + 1)
        log.silence("datafiles", allow_warning=True)

        if self.option("root"):
            os.chdir(self.option("root"))

        utils.locate_models()
        for page in models.Page.objects.all():
            page.clean(force=True)


application = Application()
application.add(ShellCommand())
application.add(RunCommand())
application.add(CleanCommand())
