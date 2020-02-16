import os

import log
from datafiles import datafile, field


log.init(debug='POMELO_DEBUG' in os.environ)
log.silence('datafiles')


@datafile
class Browser:
    name: str = ''
    width: int = 1920
    height: int = 1080
    headless: bool = False


@datafile
class Site:
    domain: str = ''
    path: str = '/'

    @property
    def url(self) -> str:
        url = f"https://{self.domain}"
        if not self.path.startswith('/'):
            self.path = '/' + self.path
        if self.path != '/':
            url += self.path
        return url


@datafile("./.pomelo.yml", defaults=True)
class Settings:
    browser: Browser = field(default_factory=Browser)
    site: Site = field(default_factory=Site)

    @property
    def label(self) -> str:
        browser = self.browser.name.capitalize()
        if self.browser.headless:
            browser += " (headless)"
        return f"{browser} -- {self.site.url}"


settings = Settings()
