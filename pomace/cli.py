# pylint: disable=no-self-use

import os
from importlib import reload

import log
from cleo.application import Application
from cleo.commands.command import Command

from . import __version__, models, prompts, server, utils
from .config import settings


class BaseCommand(Command):  # pragma: no cover
    def handle(self):
        self.configure_logging()
        self.set_directory()
        self.update_settings()
        utils.launch_browser()
        utils.locate_models()
        try:
            self.run()
        except KeyboardInterrupt:
            log.debug("User cancelled loop")
        finally:
            utils.quit_browser()
            prompts.linebreak()

    def configure_logging(self):
        log.reset()
        shift = 2 if self._command.name == "exec" else 1
        log.init(verbosity=self.io.verbosity + shift)
        log.silence("datafiles", allow_warning=True)
        log.silence("urllib3.connectionpool", allow_error=True)

    def set_directory(self):
        if self.option("root"):
            os.chdir(self.option("root"))

    def update_settings(self):
        if self.option("browser"):
            settings.browser.name = self.option("browser").lower()
        prompts.browser_if_unset()

        settings.browser.headless = self.option("headless")

        if self.argument("domain"):
            if "://" in self.argument("domain"):
                settings.url = self.argument("domain")
            else:
                settings.url = "http://" + self.argument("domain")
        domains = list(set(p.domain for p in models.Page.objects.all()))
        prompts.url_if_unset(domains)


class AliasCommand(BaseCommand):
    """
    Map one domain's site definitions to another

    alias
        {source : Domain to map to another}
        {target : Domain with existing models}
    """

    def handle(self):
        self.configure_logging()
        source = self.argument("source")
        target = self.argument("target")
        settings.aliases[source] = target
        self.line(
            f"<fg=white;options=bold>{source}</> mapped to "
            f"<fg=white;options=bold>{target}</>"
        )


class CleanCommand(BaseCommand):
    """
    Remove unused actions in local site definitions

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


class CloneCommand(BaseCommand):
    """
    Download site definitions from a git repository

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


class ExecCommand(BaseCommand):  # pragma: no cover
    """
    Run a Python script

    exec
        {script : Path to a Python script}
        {--b|browser= : Browser to use for automation}
        {--d|headless : Run the specified browser in a headless mode}
        {--r|root= : Path to directory to containing models}
    """

    def update_settings(self):
        prompts.browser_if_unset()

        if self.option("browser"):
            settings.browser.name = self.option("browser").lower()

        settings.browser.headless = self.option("headless")

    def run(self):
        utils.run_script(self.argument("script"))


class RunCommand(BaseCommand):  # pragma: no cover
    """
    Start the command-line interface

    run
        {domain? : Starting domain for the automation}
        {--b|browser= : Browser to use for automation}
        {--d|headless : Run the specified browser in a headless mode}
        {--p|prompt=* : Prompt for secrets before running}
        {--r|root= : Path to directory to containing models}
    """

    def run(self):
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


class ShellCommand(BaseCommand):  # pragma: no cover
    """
    Launch an interactive shell

    shell
        {domain? : Starting domain for the automation}
        {--b|browser= : Browser to use for automation}
        {--d|headless : Run the specified browser in a headless mode}
        {--r|root= : Path to directory to containing models}
    """

    def run(self):
        prompts.shell()


class ServeCommand(BaseCommand):
    """
    Start the web API interaface

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


application = Application("pomace", __version__)
application.add(AliasCommand())
application.add(CleanCommand())
application.add(CloneCommand())
application.add(ExecCommand())
application.add(RunCommand())
application.add(ServeCommand())
application.add(ShellCommand())
