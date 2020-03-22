import os
from typing import List, Optional
from urllib.parse import urlparse

import log
from datafiles import datafile, field

from . import shared


if 'POMACE_DEBUG' in os.environ:
    log.init(debug=True)
else:
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
    domain: str = ''
    data: List[Secret] = field(
        default_factory=lambda: [Secret('username', ''), Secret('password', '')]
    )

    @property
    def url(self) -> str:
        return f'http://{self.domain}'


@datafile("./.pomace.yml", defaults=True)
class Settings:
    browser: Browser = field(default_factory=Browser)
    url: str = ''
    secrets: List[Site] = field(default_factory=list)

    development_mode_enabled = False

    def __getattr__(self, name):
        if not name.startswith('_'):
            value = self.get_secret(name)
            if value is not None:
                return value
        return object.__getattribute__(self, name)

    def set_secret(self, name, value):
        site = self._get_site(create=True)
        assert site
        for secret in site.data:
            if secret.name == name:
                secret.value = value
                self.datafile.save()
                break
        else:
            site.data.append(Secret(name, value))

    def get_secret(self, name) -> Optional[str]:
        domain = urlparse(shared.browser.url).netloc
        for site in self.secrets:
            if site.domain == domain:
                for secret in site.data:
                    if secret.name == name:
                        return secret.value
        log.info(f'Secret {name!r} not set for {domain}')
        return None

    def update_secret(self, name, value):
        site = self._get_site()
        if site:
            for secret in site.data:
                if secret.name == name:
                    secret.value = value
                    self.datafile.save()
            log.info(f'Secret {name!r} not set for {site.domain}')

    def _get_site(self, domain='', *, create=False) -> Optional[Site]:
        domain = domain or urlparse(shared.browser.url).netloc

        for site in self.secrets:
            if site.domain == domain:
                return site

        if create:
            site = Site(domain)
            self.secrets.append(site)
            return site

        return None


settings = Settings()
