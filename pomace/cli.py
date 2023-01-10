# pylint: disable=no-self-use

import os
from importlib import reload

import log
from cleo.application import Application
from cleo.commands.command import Command
from cleo.helpers import argument, option
from startfile import startfile

from . import __version__, models, prompts, server, utils
from .config import settings


class BaseCommand(Command):
    def _run(self):
        pass

    def handle(self):
        self.configure_logging()
        self.set_directory()
        utils.locate_models()
        self.update_settings()
        utils.launch_browser()
        try:
            self._run()
        except KeyboardInterrupt:
            log.debug("User cancelled loop")
        finally:
            utils.close_browser()
            prompts.linebreak()

    def configure_logging(self):
        log.reset()
        # TODO: Rewrite for cleo 2.0 and add a test
        # shift = 2 if self.name == "exec" else 1
        # log.init(verbosity=self.io.output.verbosity + shift)
        log.silence("datafiles", allow_warning=True)
        log.silence("urllib3.connectionpool", allow_error=True)

    def set_directory(self):
        if self.option("root"):
            os.chdir(self.option("root"))

    def update_settings(self):
        if self.option("framework"):
            settings.framework = self.option("framework").lower()
        prompts.framework_if_unset()

        if self.option("browser"):
            settings.browser.name = self.option("browser").lower()
        prompts.browser_if_unset()

        settings.browser.headless = self.option("headless")

        if self.name == "exec":
            return

        if self.argument("domain"):
            if "://" in self.argument("domain"):
                settings.url = self.argument("domain")
            elif "." in self.argument("domain"):
                settings.url = "http://" + self.argument("domain")
            else:
                settings.url = ""
        domains = sorted(set(p.domain for p in models.Page.objects.all()))
        prompts.url_if_unset(domains)


class AliasCommand(BaseCommand):
    name = "alias"
    description = "Map one domain's site definitions to another."
    arguments = [
        argument(
            "source",
            description="Domain to map to another.",
        ),
        argument(
            "target",
            description="Domain with existing models.",
        ),
    ]

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
    name = "clean"
    description = "Remove unused actions in local site definitions."
    arguments = [
        argument(
            "domain",
            description="Limit cleaning to a single domain.",
            optional=True,
        ),
    ]
    options = [
        option(
            "root",
            "r",
            description="Path to directory to containing models.",
        )
    ]

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
    name = "clone"
    description = "Download site definitions from a Git repository."
    arguments = [
        argument(
            "url",
            description="Git repository URL containing pomace models.",
        ),
        argument(
            "domain",
            description="Name of sites directory for this repository.",
            optional=True,
        ),
    ]
    options = [
        option(
            "force",
            "f",
            description="Overwrite uncommitted changes in cloned repositories.",
        ),
        option(
            "root",
            "r",
            description="Path to directory to containing models.",
        ),
    ]

    def handle(self):
        self.configure_logging()
        self.set_directory()
        utils.locate_models()
        utils.clone_models(
            self.argument("url"),
            domain=self.argument("domain"),
            force=self.option("force"),
        )


class EditCommand(BaseCommand):
    name = "edit"
    description = "Open the configuration file for editing."

    def handle(self):
        startfile(settings.datafile.path)


class ExecCommand(BaseCommand):
    name = "exec"
    description = "Run a Python script with 'pomace' dependency."
    arguments = [
        argument(
            "script",
            description="Path to a Python script.",
        ),
    ]
    options = [
        option(
            "framework",
            "f",
            description="Framework to control browsers.",
            flag=False,
        ),
        option(
            "browser",
            "b",
            description="Browser to use for automation.",
            flag=False,
        ),
        option(
            "headless",
            "d",
            description="Run the specified browser in a headless mode.",
        ),
        option(
            "root",
            "r",
            description="Path to directory to containing models.",
        ),
    ]

    def _run(self):
        utils.run_script(self.argument("script"))


class RunCommand(BaseCommand):
    name = "run"
    description = "Start the command-line interface."
    arguments = [
        argument(
            "domain",
            description="Name of sites directory for this repository.",
            optional=True,
        ),
    ]
    options = [
        option(
            "framework",
            "f",
            description="Framework to control browsers.",
            flag=False,
        ),
        option(
            "browser",
            "b",
            description="Browser to use for automation.",
            flag=False,
        ),
        option(
            "headless",
            "d",
            description="Run the specified browser in a headless mode.",
        ),
        option(
            "prompt",
            "p",
            description="Prompt for secrets before running.",
            flag=False,
            multiple=True,
        ),
        option(
            "root",
            "r",
            description="Path to directory to containing models.",
        ),
    ]

    def _run(self):
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


class ShellCommand(BaseCommand):
    name = "shell"
    description = "Launch an interactive shell."
    arguments = [
        argument(
            "domain",
            description="Name of sites directory for this repository.",
            optional=True,
        ),
    ]
    options = [
        option(
            "framework",
            "f",
            description="Framework to control browsers.",
            flag=False,
        ),
        option(
            "browser",
            "b",
            description="Browser to use for automation.",
            flag=False,
        ),
        option(
            "headless",
            "d",
            description="Run the specified browser in a headless mode.",
        ),
        option(
            "root",
            "r",
            description="Path to directory to containing models.",
        ),
    ]

    def _run(self):
        prompts.shell()


class ServeCommand(BaseCommand):
    name = "serve"
    description = "Start the web API interface."
    arguments = [
        argument(
            "domain",
            description="Name of sites directory for this repository.",
            optional=True,
        ),
    ]
    options = [
        option(
            "framework",
            "f",
            description="Framework to control browsers.",
            flag=False,
        ),
        option(
            "browser",
            "b",
            description="Browser to use for automation.",
            flag=False,
        ),
        option(
            "headless",
            "d",
            description="Run the specified browser in a headless mode.",
        ),
        option(
            "prompt",
            "p",
            description="Prompt for secrets before running.",
            flag=False,
            multiple=True,
        ),
        option(
            "root",
            "r",
            description="Path to directory to containing models.",
        ),
        option(
            "debug",
            description="Run the server in debug mode.",
        ),
    ]

    def handle(self):
        self.configure_logging()
        self.set_directory()
        self.update_settings()
        prompts.bullet = None
        utils.locate_models()
        try:
            server.app.run(debug=self.option("debug"))
        finally:
            utils.close_browser()


application = Application("pomace", __version__)
application.add(AliasCommand())
application.add(CleanCommand())
application.add(CloneCommand())
application.add(EditCommand())
application.add(ExecCommand())
application.add(RunCommand())
application.add(ServeCommand())
application.add(ShellCommand())
