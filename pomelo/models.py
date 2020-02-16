import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional
from urllib.parse import urlparse

import log
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
    name: str = '<action>'
    locators: List[Locator] = field(
        default_factory=lambda: [Locator('<mode>', '<value>')]
    )

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


@datafile("./.pomelo/{self.domain}/{self.path}/{self.variant}.yml", defaults=True)
class Page:

    domain: str
    path: str = '@'
    variant: str = 'default'

    active_locators: List[Locator] = field(
        default_factory=lambda: [Locator('<mode>', '<value>')]
    )
    inactive_locators: List[Locator] = field(default_factory=list)

    actions: List[Action] = field(default_factory=lambda: [Action()])

    @classmethod
    def at(cls, url: str, *, variant: str = 'default') -> 'Page':
        if shared.browser.url != url:
            log.info(f"Visiting {url}")
            shared.browser.visit(url)

        if shared.browser.url != url:
            log.info(f"Redirected to {url}")

        parts = urlparse(shared.browser.url)
        path = '@' + parts.path.strip('/').replace('/', '@')

        return cls(domain=parts.netloc, path=path, variant=variant)  # type: ignore

    def __repr__(self):
        return f"Page.at('{self.url}', variant='{self.variant}')"

    def __str__(self):
        if self.variant == 'default':
            return self.url
        return f'{self.url} ({self.variant})'

    def __dir__(self):
        return [str(action) for action in self.actions]

    def __getattr__(self, name: str) -> Action:
        if '_' not in name:
            raise AttributeError

        verb, name = name.split('_', 1)

        for action in self.actions:
            if action.name == name and action.verb == verb:
                return action

        if Verb.validate(verb):
            action = Action(verb, name)
            self.actions.append(action)
            return action

        raise AttributeError(f'No such action: {name}')

    @property
    def url(self) -> str:
        path = self.path.replace('@', '/')
        return f'https://{self.domain}{path}'

    @property
    def active(self) -> bool:
        match = shared.browser.url.rstrip('/') == self.url.rstrip('/')

        for locator in self.active_locators:
            if locator.mode and not locator.find():
                log.debug(f'{self}: Unable to find: {locator}')
                match = False

        for locator in self.inactive_locators:
            if locator.mode and locator.find():
                log.debug(f'{self}: Found unexpected: {locator}')
                match = False

        return match

    def perform(self, name: str, *, prompt: Callable) -> 'Page':
        action = getattr(self, name)
        try:
            page = action()
        except TypeError:
            value = prompt()
            page = action(value)
        return page
