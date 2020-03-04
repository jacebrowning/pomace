from typing import Callable, List, Tuple
from urllib.parse import urlparse

import log
from datafiles import datafile, field
from parse import parse
from splinter.driver import ElementAPI

from . import shared
from .config import settings
from .enums import Mode, Verb


class URL:

    SLASH = '∕'  # 'DIVISION SLASH' (U+2215)

    def __init__(self, url_or_domain, path=None):
        if path:
            self.value = f'https://{url_or_domain}' + path.replace(self.SLASH, '/')
        else:
            self.value = str(url_or_domain)

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if self.domain != other.domain:
            return False
        if self.path == other.path:
            return True
        result = parse(self.path, other.path)
        if not result:
            return False
        for value in result.named.values():
            if '/' in value:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def domain(self) -> str:
        return urlparse(self.value).netloc

    @property
    def path(self) -> str:
        return '/' + urlparse(self.value).path.strip('/')

    @property
    def path_encoded(self) -> str:
        return self.path.replace('/', self.SLASH)


@datafile(order=True)
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


@datafile
class Action:

    verb: str = ''
    name: str = ''
    locators: List[Locator] = field(default_factory=lambda: [Locator()])

    @property
    def _verb(self) -> Verb:
        return Verb(self.verb)

    def __str__(self):
        return f'{self.verb}_{self.name}'

    def __bool__(self) -> bool:
        return bool(self.verb and self.name)

    def __call__(self, *args, **kwargs) -> 'Page':
        page = kwargs.pop('_page', None)
        for locator in self.locators:

            # TODO: https://github.com/jacebrowning/datafiles/issues/22
            if isinstance(locator, dict):
                locator = Locator(**locator)

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


@datafile("./.pomace/{self.domain}/{self.path}/{self.variant}.yml", defaults=True)
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

        return cls(domain=URL(url).domain, path=URL(url).path_encoded, variant=variant)

    @property
    def url(self) -> URL:
        return URL(self.domain, self.path)

    @property
    def active(self) -> bool:
        log.debug(f'Determining if active: {self!r}')

        if self.url != URL(shared.browser.url):
            log.debug(
                f'{self!r} is inactive - URL does not match: {shared.browser.url}'
            )
            return False

        for locator in self.active_locators:
            if locator and not locator.find():
                log.debug(f'{self!r} is inactive - Unable to find: {locator!r}')
                return False

        for locator in self.inactive_locators:
            if locator and locator.find():
                log.debug(f'{self!r} is inactive - Found unexpected: {locator!r}')
                return False

        log.debug(f'{self!r} is active')
        return True

    def __repr__(self):
        if self.variant == 'default':
            return f"Page.at('{self.url.value}')"
        return f"Page.at('{self.url.value}', variant='{self.variant}')"

    def __str__(self):
        if self.variant == 'default':
            return f'{self.url}'
        return f'{self.url} ({self.variant})'

    def __dir__(self):
        names = []
        add_placeholder = True
        for action in self.actions:
            if action:
                names.append(str(action))
            else:
                add_placeholder = False
        if add_placeholder:
            self.actions.append(Action())
        return names

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

    def perform(self, name: str, *, prompt: Callable) -> Tuple['Page', bool]:
        action = getattr(self, name)
        if action.verb in {'fill', 'select'}:
            try:
                value = getattr(settings, action.name)
            except AttributeError:
                value = prompt()
            page = action(value, _page=self)
        else:
            page = action(_page=self)
        return page, page != self


def autopage() -> Page:
    matching_pages = []

    url = urlparse(shared.browser.url)
    for page in Page.objects.filter(domain=url.netloc):
        if page.active:
            matching_pages.append(page)

    if matching_pages:
        if len(matching_pages) > 1:
            for page in matching_pages:
                log.warn(f'Multiple pages matched: {page}')
        return matching_pages[0]

    log.warn('Creating new page as none matched')
    page = Page.at(shared.browser.url)
    page.datafile.save()
    return page
