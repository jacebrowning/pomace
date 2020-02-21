import os
from typing import List
from urllib.parse import urlparse

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
class Secret:
    name: str
    value: str


@datafile
class Site:
    url: str = ''

    @property
    def domain(self) -> str:
        return urlparse(self.url).netloc


@datafile("./.pomelo.yml", defaults=True)
class Settings:
    browser: Browser = field(default_factory=Browser)
    site: Site = field(default_factory=Site)
    secrets: List[Secret] = field(
        default_factory=lambda: [Secret('password', '<value>')]
    )

    def __repr__(self):
        secrets = ', '.join([secret.name for secret in self.secrets])
        return f'<{self.site.domain} secrets: {secrets}>'

    def __getattr__(self, name):
        for secret in self.secrets:
            if secret.name == name:
                return secret.value
        return object.__getattribute__(self, name)


settings = Settings()
