# pylint: disable=no-self-use

import os
from importlib import reload

from bullet import Bullet, Input
from cleo import Application, Command

from . import browser, models, utils
from .config import settings


class RunCommand(Command):
    """
    Run pomace in a loop

    run
        {--browser= : Browser to use for automation}
        {--headless : If set, the specified browser will run headless}
        {--domain= : Starting domain for the automation}
        {--r|root= : Directory to load models from}
    """

    def handle(self):
        self.update_settings()
        self.launch_browser()
        try:
            self.run_loop()
        finally:
            utils.quit_browser()

    def update_settings(self):
        if self.option('root'):
            os.chdir(self.option('root'))

        if self.option('browser'):
            settings.browser.name = self.option('browser').lower()

        settings.browser.headless = self.option('headless')

        if self.option('domain'):
            settings.site.url = "https://" + self.option('domain')

    def launch_browser(self):
        if not settings.browser.name:
            cli = Bullet(
                prompt="\nSelect a browser for automation: ",
                bullet=" ● ",
                choices=browser.NAMES,
            )
            settings.browser.name = cli.launch().lower()

        if not settings.site.domain:
            domains = [p.domain for p in models.Page.objects.all()]
            if domains:
                cli = Bullet(
                    prompt="\nStarting domain: ",
                    bullet=" ● ",
                    choices=list(set(domains)),
                )
            else:
                cli = Input(prompt="\nStarting domain: ", strip=True)
            settings.site.url = f'https://{cli.launch()}'

        utils.launch_browser()

    def run_loop(self):
        page = models.autopage()
        self.clear_screen()
        self.display_url(page)
        while True:
            choices = ['<reload>'] + dir(page)
            cli = Bullet(prompt=f"\nSelect an action: ", bullet=" ● ", choices=choices)
            action = cli.launch()
            if action == '<reload>':
                reload(models)
                page = models.autopage()
                self.clear_screen()
                self.display_url(page)
                continue

            cli = Input(prompt=f"\nValue: ")
            page, transitioned = page.perform(action, prompt=cli.launch)
            if transitioned:
                self.clear_screen()
                self.display_url(page)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_url(self, page):
        self.line(f'<fg=white;options=bold>{page}</>')


application = Application()
application.add(RunCommand())
