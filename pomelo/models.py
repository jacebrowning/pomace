from dataclasses import dataclass, field
from typing import List
from urllib.parse import urlparse

from datafiles import datafile


@dataclass
class Action:

    name: str


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

    @property
    def action_names(self) -> List[str]:
        return [action.name for action in self.actions]
