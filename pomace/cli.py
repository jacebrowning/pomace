# pylint: disable=no-self-use

import os
from importlib import import_module, reload

import log
from cleo import Application, Command
from IPython import embed

from . import browser, models, shared, utils
from .config import settings


def prompt_for_browser_if_unset():
    if settings.browser.name:
        return

    if "CI" in os.environ or not shared.cli:
        settings.browser.name = os.getenv("BROWSER", "firefox")
        return

    command = shared.cli.Bullet(
        prompt="\nSelect a browser for automation: ",
        bullet=" ● ",
        choices=browser.NAMES,
    )
    settings.browser.name = command.launch().lower()


def prompt_for_url_if_unset():
    if settings.url:
        return

    if "CI" in os.environ or not shared.cli:
        settings.url = "http://example.com"
        return

    domains = [p.domain for p in models.Page.objects.all()]
    if domains:
        command = shared.cli.Bullet(
            prompt="\nStarting domain: ", bullet=" ● ", choices=list(set(domains))
        )
    else:
        command = shared.cli.Input(prompt="\nStarting domain: ", strip=True)
    domain = command.launch()
    settings.url = f"https://{domain}"


def prompt_for_secret_if_unset(name: str):
    if settings.get_secret(name, _log=False):
        return

    if "CI" in os.environ or not shared.cli:
        settings.set_secret(name, "<unset>")
        return

    command = shared.cli.Input(prompt=f"{name}: ")
    value = command.launch()
    settings.set_secret(name, value)


class BaseCommand(Command):
    def handle(self):
        log.reset()
        log.init(verbosity=self.io.verbosity + 1)
        log.silence("datafiles", allow_warning=True)
        self.update_settings()
        prompt_for_browser_if_unset()
        prompt_for_url_if_unset()
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
