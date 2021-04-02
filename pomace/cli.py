# pylint: disable=no-self-use

import os
from importlib import reload

import log
from cleo import Application, Command

from . import models, prompts, server, utils
from .config import settings


class BaseCommand(Command):  # pragma: no cover
    def handle(self):
        self.configure_logging()
        self.set_directory()
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

    def configure_logging(self):
        log.reset()
        log.init(verbosity=self.io.verbosity + 1)
        log.silence("datafiles", allow_warning=True)
        log.silence("urllib3.connectionpool", allow_error=True)

    def set_directory(self):
        if self.option("root"):
            os.chdir(self.option("root"))

    def update_settings(self):
        if self.option("browser"):
            settings.browser.name = self.option("browser").lower()

        settings.browser.headless = self.option("headless")

        if self.argument("domain"):
            if "://" in self.argument("domain"):
                settings.url = self.argument("domain")
            else:
                settings.url = "http://" + self.argument("domain")


class CloneCommand(BaseCommand):
    """
    Download a site definition from a Git repository

    clone
        {url : Git repository URL containing pomace models}
        {domain? : Name of sites directory for this repository}
        {--f|force : Overwrite uncommitted changes in cloned repositories}
        {--r|root= : Path to directory to containing models}
    """

    def handle(self):
        self.configure_logging()
        self.set_directory()
        utils.locate_models()
        utils.clone_models(
            self.argument("url"),
            domain=self.argument("domain"),
            force=self.option("force"),
        )


class ShellCommand(BaseCommand):  # pragma: no cover
    """
    Launch an interactive shell

    shell
        {domain? : Starting domain for the automation}
        {--b|browser= : Browser to use for automation}
        {--d|headless : Run the specified browser in a headless mode}
        {--r|root= : Path to directory to containing models}
    """

    def run_loop(self):
        prompts.shell()


class RunCommand(BaseCommand):  # pragma: no cover
    """
    Run pomace in a loop

    run
        {domain? : Starting domain for the automation}
        {--b|browser= : Browser to use for automation}
        {--d|headless : Run the specified browser in a headless mode}
        {--p|prompt=* : Prompt for secrets before running}
        {--r|root= : Path to directory to containing models}
    """

    def run_loop(self):
        for name in self.option("prompt"):
            prompts.secret_if_unset(name)

        self.clear_screen()
        page = models.auto()
        self.display_url(page)

        while True:
            action = prompts.action(page)
            if action:
                page, transitioned = page.perform(action)
                if transitioned:
                    self.clear_screen()
                    self.display_url(page)
            else:
                reload(models)
                self.clear_screen()
                page = models.auto()
                self.display_url(page)

    def clear_screen(self):
        os.system("cls" if os.name == "nt" else "clear")

    def display_url(self, page):
        self.line(f"<fg=white;options=bold>{page}</>")
        prompts.linebreak(force=True)


class ServeCommand(BaseCommand):
    """
    Run pomace in service mode

    serve
        {domain? : Starting domain for the automation}
        {--b|browser= : Browser to use for automation}
        {--d|headless : Run the specified browser in a headless mode}
        {--p|prompt=* : Prompt for secrets before running}
        {--r|root= : Path to directory to containing models}
        {--debug : Run the server in debug mode}
    """

    def handle(self):
        self.configure_logging()
        self.set_directory()
        self.update_settings()
        prompts.bullet = None
        utils.locate_models()
        try:
            server.app.run(debug=self.option("debug"))
        finally:
            utils.quit_browser()


class CleanCommand(BaseCommand):
    """
    Remove all unused actions and locators

    clean
        {domain? : Limit cleaning to a single domain}
        {--r|root= : Path to directory to containing models}
    """

    def handle(self):
        self.configure_logging()
        self.set_directory()
        utils.locate_models()
        if self.argument("domain"):
            pages = models.Page.objects.filter(domain=self.argument("domain"))
        else:
            pages = models.Page.objects.all()
        for page in pages:
            page.clean(force=True)


application = Application()
application.add(CloneCommand())
application.add(ShellCommand())
application.add(RunCommand())
application.add(ServeCommand())
application.add(CleanCommand())
