import log

from datafiles import datafile, field


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


settings = Settings()
