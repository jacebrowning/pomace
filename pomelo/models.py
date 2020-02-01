from __future__ import annotations

from typing import List
from urllib.parse import urlparse

from datafiles import datafile


@datafile("./.pomelo/{self.domain}{self.path}/{self.variant}.yml")
class Page:

    domain: str
    path: str = '/'
    variant: str = 'default'

    @classmethod
    def from_url(cls, url: str) -> Page:
        parts = urlparse(url)
        return cls(domain=parts.netloc, path=parts.path)  # type: ignore

    @property
    def actions(self) -> List[str]:
        return ['foo', 'bar']
