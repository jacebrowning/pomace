from dataclasses import dataclass, field
from typing import Callable, List
from urllib.parse import urlparse

import log
from datafiles import datafile
from splinter.driver import ElementAPI

from . import shared
from .enums import Mode, Verb


class URL:

    SLASH = '∕'  # 'DIVISION SLASH' (U+2215)

    def __init__(self, url_or_domain, path=None):
        if path:
            self.value = f'https://{url_or_domain}' + path.replace(self.SLASH, '/')
        else:
            self.value = str(url_or_domain)

    def __eq__(self, other):
        return self.domain == other.domain and self.path == other.path

    def __ne__(self, other):
        return self.domain != other.domain or self.path != other.path

    @property
    def domain(self) -> str:
        return urlparse(self.value).netloc

    @property
    def path(self) -> str:
        return '/' + urlparse(self.value).path.strip('/')

    @property
    def path_encoded(self) -> str:
        return self.path.replace('/', self.SLASH)


@dataclass(order=True)
class Locator:

    mode: str = ''
    value: str = ''
    uses: int = field(default=0, compare=True)

    @property
    def _mode(self) -> Mode:
        return Mode(self.mode)

    def __bool__(self) -> bool:
        return bool(self.mode and self.value)

    def find(self) -> ElementAPI:
        return self._mode.finder(self.value)


@dataclass
class Action:

    verb: str = ''
    name: str = ''
    locators: List[Locator] = field(default_factory=lambda: [Locator()])

    @property
    def _verb(self) -> Verb:
        return Verb(self.verb)

    def __bool__(self) -> bool:
        return bool(self.verb and self.name)

    def __str__(self):
        return f'{self.verb}_{self.name}'

    def __call__(self, *args, **kwargs) -> 'Page':
        page = kwargs.pop('_page', None)
        for locator in self.locators:

            # TODO: https://github.com/jacebrowning/datafiles/issues/22
            if not hasattr(locator, 'find'):
                locator = Locator(**locator)  # type: ignore

            if not locator:
                continue

            log.debug(f'Using {locator} to find {self.name!r}')
            element = locator.find()
            if element:
                log.debug(f'Locator found element: {element}')
            else:
                log.debug(f'Locator unable to find element')
                continue

            self._perform_action(element, *args, **kwargs)
            locator.uses += 1
            break

        else:
            log.error(f'No locators able to find {self.name!r}')
            if page:
                return page

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
    path: str = URL.SLASH
    variant: str = 'default'

    active_locators: List[Locator] = field(default_factory=lambda: [Locator()])
    inactive_locators: List[Locator] = field(default_factory=lambda: [Locator()])

    actions: List[Action] = field(default_factory=lambda: [Action()])

    @classmethod
    def at(cls, url: str, *, variant: str = 'default') -> 'Page':
        if shared.browser.url != url:
            log.info(f"Visiting {url}")
            shared.browser.visit(url)

        if shared.browser.url != url:
            log.info(f"Redirected to {url}")

        return cls(
            domain=URL(url).domain, path=URL(url).path_encoded, variant=variant
        )  # type: ignore

    def __repr__(self):
        if self.variant == 'default':
            return f"Page.at('{self.url.value}')"
        return f"Page.at('{self.url.value}', variant='{self.variant}')"

    def __str__(self):
        if self.variant == 'default':
            return self.url.value
        return f'{self.url} ({self.variant})'

    def __dir__(self):
        return [str(action) for action in self.actions]

    def __getattr__(self, name: str) -> Action:
        if '_' in name:
            verb, name = name.split('_', 1)

            for action in self.actions:
                if action.name == name and action.verb == verb:
                    return action

            if Verb.validate(verb):
                action = Action(verb, name)
                self.actions.append(action)
                return action

        return object.__getattribute__(self, name)

    @property
    def url(self) -> URL:
        return URL(self.domain, self.path)

    @property
    def active(self) -> bool:
        log.debug(f'Determining if active: {self!r}')

        if URL(shared.browser.url) != self.url:
            log.debug(f'Inactive - URL does not match: {shared.browser.url}')
            return False

        for locator in self.active_locators:
            if locator and not locator.find():
                log.debug(f'Inactive - Unable to find: {locator!r}')
                return False

        for locator in self.inactive_locators:
            if locator and locator.find():
                log.debug(f'Inactive - Found unexpected: {locator!r}')
                return False

        log.debug('Active')
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

    log.warn('Creating new page as none matched')
    page = Page.at(shared.browser.url)
    page.datafile.save()  # type: ignore
    return page
