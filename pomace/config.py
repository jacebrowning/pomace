from typing import List, Optional

import log
from datafiles import datafile, field

from . import shared
from .types import URL


log.silence('datafiles', allow_warning=True)


@datafile
class Browser:
    name: str = ''
    width: int = 1366
    height: int = 768
    headless: bool = False


@datafile
class Secret:
    name: str
    value: str


@datafile
class Site:
    domain: str
    data: List[Secret] = field(
        default_factory=lambda: [Secret('username', ''), Secret('password', '')]
    )

    @property
    def url(self) -> str:
        return f'http://{self.domain}'


@datafile("./pomace.yml", defaults=True)
class Settings:
    browser: Browser = field(default_factory=Browser)
    url: str = ''
    secrets: List[Site] = field(default_factory=list)

    def __getattr__(self, name):
        return self.get_secret(name) or object.__getattribute__(self, name)

    def get_secret(self, name) -> Optional[str]:
        domain = URL(shared.browser.url).domain
        for site in self.secrets:
            if site.domain == domain:
                for secret in site.data:
                    if secret.name == name:
                        return secret.value
        log.info(f'Secret {name!r} not set for {domain}')
        return None

    def set_secret(self, name, value):
        domain = URL(shared.browser.url).domain
        site = self._get_site(domain, create=True)
        if site:
            for secret in site.data:
                if secret.name == name:
                    secret.value = value
                    break
            else:
                site.data.append(Secret(name, value))

    def update_secret(self, name, value):
        domain = URL(shared.browser.url).domain
        site = self._get_site(domain)
        if site:
            for secret in site.data:
                if secret.name == name:
                    secret.value = value
                    return
        log.info(f'Secret {name!r} not set for {domain}')

    def _get_site(self, domain: str, *, create=False) -> Optional[Site]:
        for site in self.secrets:
            if site.domain == domain:
                return site

        if create:
            site = Site(domain)
            self.secrets.append(site)
            return site

        return None


settings = Settings()
