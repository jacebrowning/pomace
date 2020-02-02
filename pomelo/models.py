from dataclasses import dataclass, field
from typing import List
from urllib.parse import urlparse

from datafiles import datafile

from .enums import Verb


@dataclass
class Action:

    verb: str = list(Verb)[0].value
    name: str = 'element'

    def __str__(self):
        return f'{self.verb}_{self.name}'


@datafile("./.pomelo/{self.domain}{self.path}/{self.variant}.yml")
class Page:

    domain: str
    path: str = '/'
    variant: str = 'default'

    actions: List[Action] = field(default_factory=list)

    @classmethod
    def from_url(cls, url: str) -> 'Page':
        parts = urlparse(url)
        return cls(domain=parts.netloc, path=parts.path)  # type: ignore
