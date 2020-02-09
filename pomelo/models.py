import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional
from urllib.parse import urlparse

from splinter.driver import ElementAPI

from datafiles import datafile

from . import shared
from .enums import Verb


@dataclass(order=True)
class Locator:

    mode: str
    value: str
    uses: int = field(default=0, compare=True)

    def find(self) -> Optional[ElementAPI]:
        return getattr(shared.browser, f'find_by_{self.mode}')(self.value)


@dataclass
class Action:

    verb: str = list(Verb)[0].value
    name: str = 'element'
    locators: List[Locator] = field(default_factory=lambda: [Locator('tag', 'body')])

    def __str__(self):
        return f'{self.verb}_{self.name}'

    def __call__(self, *args, **kwargs) -> 'Page':
        for locator in self.locators:

            # TODO: https://github.com/jacebrowning/datafiles/issues/22
            if not hasattr(locator, 'find'):
                locator = Locator(**locator)  # type: ignore

            element = locator.find()
            if not element:
                continue

            try:
                function = getattr(element, self.verb)
            except AttributeError:
                continue

            function(*args, **kwargs)
            locator.uses += 1
            break

        time.sleep(Verb(self.verb).delay)

        return Page.at(shared.browser.url)


@datafile("./.pomelo/{self.domain}{self.path}/{self.variant}.yml", defaults=True)
class Page:

    domain: str
    path: str = '/'
    variant: str = 'default'

    active_locators: List[Locator] = field(
        default_factory=lambda: [Locator('tag', 'body')]
    )
    inactive_locators: List[Locator] = field(
        default_factory=lambda: [Locator('tag', 'body')]
    )

    actions: List[Action] = field(default_factory=lambda: [Action()])

    @classmethod
    def at(cls, url: str) -> 'Page':
        parts = urlparse(url)
        return cls(domain=parts.netloc, path=parts.path)  # type: ignore

    def __repr__(self):
        return f"Page.at('{self}')"

    def __str__(self):
        if self.variant == 'default':
            if self.path == '/':
                return f'https://{self.domain}'
            return f'https://{self.domain}{self.path}'
        if self.path == '/':
            return f'https://{self.domain} ({self.variant})'
        return f'https://{self.domain}{self.path} ({self.variant})'

    def __dir__(self):
        return [str(action) for action in self.actions]

    def __getattr__(self, name: str) -> Action:
        verb, name = name.split('_', 1)

        for action in self.actions:
            if action.name == name and action.verb == verb:
                return action

        if Verb.validate(verb):
            action = Action(verb, name)
            self.actions.append(action)
            return action

        raise AttributeError(f'No such action: {name}')

    def perform(self, name: str, *, prompt: Callable) -> 'Page':
        action = getattr(self, name)
        try:
            page = action()
        except TypeError:
            value = prompt()
            page = action(value)
        return page
