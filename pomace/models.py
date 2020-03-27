from typing import Callable, List, Tuple

import log
from datafiles import datafile, field
from splinter.driver import ElementAPI

from . import shared
from .config import settings
from .enums import Mode, Verb
from .types import URL


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
        add_placeholder = settings.development_mode_enabled
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

            if Verb.validate(verb) and settings.development_mode_enabled:
                action = Action(verb, name)
                self.actions.append(action)
                return action

        return object.__getattribute__(self, name)

    def perform(self, name: str, *, prompt: Callable) -> Tuple['Page', bool]:
        action = getattr(self, name)
        if action.verb in {'fill', 'select'}:
            value = settings.get_secret(action.name) or prompt()
            settings.update_secret(action.name, value)
            page = action(value, _page=self)
        else:
            page = action(_page=self)
        return page, page != self


def autopage() -> Page:
    matching_pages = []

    for page in Page.objects.filter(domain=URL(shared.browser.url).domain):
        if page.active:
            matching_pages.append(page)

    if matching_pages:
        if len(matching_pages) > 1:
            for page in matching_pages:
                log.warn(f'Multiple pages matched: {page}')
        return matching_pages[0]

    if settings.development_mode_enabled:
        log.info(f'Creating new page: {shared.browser.url}')
        page = Page.at(shared.browser.url)
        return page

    raise RuntimeError('No matching page')
