import os

import log

from datafiles import datafile, field


log.init(debug='POMELO_DEBUG' in os.environ)
log.silence('datafiles')


@datafile
class Browser:
    name: str = ''
    headless: bool = False


@datafile
class Site:
    domain: str = ''


@datafile("./.pomelo.yml")
class Settings:
    browser: Browser = field(default_factory=Browser)
    site: Site = field(default_factory=Site)

    @property
    def label(self) -> str:
        browser = self.browser.name.capitalize()
        if self.browser.headless:
            browser += " (headless)"
        url = f"https://{self.site.domain}"
        return f"{browser} -- {url}"


settings = Settings()
