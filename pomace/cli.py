# pylint: disable=no-self-use

import os
from importlib import reload

import log
from cleo import Application, Command

from . import browser, models, utils
from .config import settings


try:
    import bullet
except ImportError:
    bullet = None  # https://github.com/Mckinsey666/bullet/issues/2
    log.warn("Interactive CLI prompts not yet supported on Windows")


def prompt_for_browser_if_unset():
    if not settings.browser.name and bullet:
        cli = bullet.Bullet(
            prompt="\nSelect a browser for automation: ",
            bullet=" ● ",
            choices=browser.NAMES,
        )
        settings.browser.name = cli.launch().lower()


def prompt_for_url_if_unset():
    if not settings.url and bullet:
        domains = [p.domain for p in models.Page.objects.all()]
        if domains:
            cli = bullet.Bullet(
                prompt="\nStarting domain: ", bullet=" ● ", choices=list(set(domains))
            )
        else:
            cli = bullet.Input(prompt="\nStarting domain: ", strip=True)
        settings.url = f"https://{cli.launch()}"


def prompt_for_secret_if_unset(name: str):
    if bullet:
        cli = bullet.Input(prompt=f"{name}: ")
        value = settings.get_secret(name) or cli.launch()
        settings.set_secret(name, value)


class RunCommand(Command):
    """
    Run pomace in a loop

    run
        {--browser= : Browser to use for automation}
        {--headless : Run the specified browser in a headless mode}
        {--domain= : Starting domain for the automation}
        {--root= : Directory to load models from}
        {--dev : Enable development mode to create missing pages}
    """

    RELOAD_ACTIONS = "<reload actions>"

    def handle(self):
        log.reset()
        log.init(verbosity=self.io.verbosity + 1)
        log.silence('datafiles', allow_warning=True)
        self.update_settings()
        prompt_for_browser_if_unset()
        prompt_for_url_if_unset()
        utils.launch_browser()
        try:
            self.run_loop()
        finally:
            utils.quit_browser()

    def update_settings(self):
        if self.option("root"):
            os.chdir(self.option("root"))

        if self.option("browser"):
            settings.browser.name = self.option("browser").lower()

        settings.browser.headless = self.option("headless")

        if self.option("domain"):
            settings.url = "https://" + self.option("domain")

        if self.option("dev"):
            settings.development_mode_enabled = True

    def run_loop(self):
        page = models.autopage()
        self.clear_screen()
        self.display_url(page)
        while True:
            choices = [self.RELOAD_ACTIONS] + dir(page)
            cli = bullet.Bullet(
                prompt=f"\nSelect an action: ", bullet=" ● ", choices=choices
            )
            action = cli.launch()
            if action == self.RELOAD_ACTIONS:
                reload(models)
                page = models.autopage()
                self.clear_screen()
                self.display_url(page)
                continue

            cli = bullet.Input(prompt=f"\nValue: ")
            page, transitioned = page.perform(action, prompt=cli.launch)
            if transitioned:
                self.clear_screen()
                self.display_url(page)

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def display_url(self, page):
        self.line(f"<fg=white;options=bold>{page}</>")


application = Application()
application.add(RunCommand())
