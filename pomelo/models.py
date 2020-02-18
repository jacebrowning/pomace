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

    mode: str
    value: str
    uses: int = field(default=0, compare=True)

    @property
    def _mode(self) -> Mode:
        return Mode(self.mode)

    @property
    def placeholder(self) -> bool:
        return self.mode.startswith('<')

    def find(self) -> ElementAPI:
        return self._mode.finder(self.value)


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
    path: str = URL.SLASH
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

        return cls(
            domain=URL(url).domain, path=URL(url).path_encoded, variant=variant
        )  # type: ignore

    def __repr__(self):
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
