from dataclasses import dataclass, field
from typing import Callable, List, Optional
from urllib.parse import urlparse

import log
from splinter.driver import ElementAPI

from datafiles import datafile

from . import shared
from .enums import Verb


@dataclass
class URL:

    _value: str

    def __eq__(self, other):
        return self.domain == other.domain and self.path == other.path

    def __ne__(self, other):
        return self.domain != other.domain or self.path != other.path

    @property
    def domain(self) -> str:
        return urlparse(self._value).netloc

    @property
    def path(self) -> str:
        return urlparse(self._value).path.strip('/')


@dataclass(order=True)
class Locator:

    mode: str
    value: str
    uses: int = field(default=0, compare=True)

    @property
    def placeholder(self) -> bool:
        return self.mode.startswith('<')

    def find(self) -> Optional[ElementAPI]:
        if self.mode.startswith('find_'):
            name = self.mode
        else:
            name = f'find_by_{self.mode}'
        try:
            finder = getattr(shared.browser, name)
        except AttributeError as e:
            log.error(e)
            return None
        else:
            return finder(self.value)


@dataclass
class Action:

    verb: str = list(Verb)[0].value
    name: str = '<action>'
    locators: List[Locator] = field(
        default_factory=lambda: [Locator('<mode>', '<value>')]
    )

    @property
    def _verb(self) -> Verb:
        return Verb(self.verb)

    def __str__(self):
        return f'{self.verb}_{self.name}'

    def __call__(self, *args, **kwargs) -> 'Page':
        page = kwargs.pop('_page', None)
        for locator in self.locators:

            # TODO: https://github.com/jacebrowning/datafiles/issues/22
            if not hasattr(locator, 'find'):
                locator = Locator(**locator)  # type: ignore

            if locator.placeholder:
                log.debug(f'Placeholder locator: {locator}')
                continue

            element = locator.find()
            if not element:
                log.debug(f'Invalid locator: {locator}')
                continue

            self._perform_action(element, *args, **kwargs)
            locator.uses += 1
            break

        else:
            log.warn(f'Unable to {self}')

        if page and self._verb.updates:
            return page

        return autopage()

    def _perform_action(self, element: ElementAPI, *args, **kwargs):
        function = getattr(element, self.verb)
        function(*args, **kwargs)
        self._verb.post_action()


@datafile("./.pomelo/{self.domain}/{self.path}/{self.variant}.yml", defaults=True)
class Page:

    domain: str
    path: str = '@'
    variant: str = 'default'

    active_locators: List[Locator] = field(
        default_factory=lambda: [Locator('<mode>', '<value>')]
    )
    inactive_locators: List[Locator] = field(
        default_factory=lambda: [Locator('<mode>', '<value>')]
    )

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
            return object.__getattribute__(self, name)

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
        log.debug(f'Determining if active: {self}')

        if URL(shared.browser.url) != URL(self.url):
            log.debug(f'Wrong URL: {shared.browser.url}')
            return False

        for locator in self.active_locators:
            if locator.placeholder:
                log.debug(f'Placeholder locator: {locator}')
                return False
            if locator.mode and not locator.find():
                log.debug(f'{self}: Unable to find: {locator}')
                return False

        for locator in self.inactive_locators:
            if locator.placeholder:
                log.debug(f'Placeholder locator: {locator}')
                return False
            if locator.mode and locator.find():
                log.debug(f'{self}: Found unexpected: {locator}')
                return False

        log.debug(f'Page is active: {self}')
        return True

    def perform(self, name: str, *, prompt: Callable) -> 'Page':
        action = getattr(self, name)
        try:
            page = action(_page=self)
        except TypeError:
            value = prompt()
            page = action(value, _page=self)
        return page


def autopage() -> Page:
    matching_pages = []

    url = urlparse(shared.browser.url)
    for page in Page.objects.filter(domain=url.netloc):  # type: ignore
        if page.active:
            matching_pages.append(page)

    if matching_pages:
        if len(matching_pages) > 1:
            for page in matching_pages:
                log.warn(f'Multiple pages matched: {page}')
        return matching_pages[0]

    log.warn('No matching pages found')
    page = Page.at(shared.browser.url)
    page.datafile.save()  # type: ignore
    return page
