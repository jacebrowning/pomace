from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse

from datafiles import datafile
from splinter.browser import Browser
from splinter.driver import ElementAPI

from .enums import Verb


@dataclass(order=True)
class Locator:

    mode: str
    value: str
    uses: int = field(default=0, compare=True)

    def find(self, *, browser: Browser) -> Optional[ElementAPI]:
        return getattr(browser, f'find_by_{self.mode}')(self.value)


@dataclass
class Action:

    verb: str = list(Verb)[0].value
    name: str = 'element'
    locators: List[Locator] = field(default_factory=list)

    def __str__(self):
        return f'{self.verb}_{self.name}'


@datafile("./.pomelo/{self.domain}{self.path}/{self.variant}.yml", defaults=True)
class Page:

    domain: str
    path: str = '/'
    variant: str = 'default'

    actions: List[Action] = field(default_factory=list)

    @classmethod
    def from_url(cls, url: str) -> 'Page':
        parts = urlparse(url)
        return cls(domain=parts.netloc, path=parts.path)  # type: ignore

    def __str__(self):
        if self.variant == 'default':
            if self.path == '/':
                return self.domain
            return f'{self.domain}{self.path}'
        if self.path == '/':
            return f'{self.domain} ({self.variant})'
        return f'{self.domain}{self.path} ({self.variant})'

    def _get_action(self, name: str) -> Action:
        verb, name = name.split('_', 1)
        for action in self.actions:
            if action.name == name and action.verb == verb:
                return action
        raise AttributeError(f'No such action: {name}')

    def perform(self, name: str, *, browser: Browser):
        action = self._get_action(name)
        for _locator in action.locators:
            # TODO: Fix 'CommentedMap' object has no attribute 'find'
            locator = Locator(**_locator)  # type: ignore
            element = locator.find(browser=browser)
            getattr(element, action.verb)()
