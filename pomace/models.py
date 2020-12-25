from contextlib import suppress
from typing import Callable, List, Optional, Tuple

import log
from bs4 import BeautifulSoup
from datafiles import datafile, field, mapper
from selenium.common.exceptions import WebDriverException
from splinter.driver.webdriver import WebDriverElement
from splinter.exceptions import ElementDoesNotExist

from . import shared
from .config import settings
from .enums import Mode, Verb
from .types import URL


__all__ = ["Locator", "Action", "Page"]


@datafile(order=True)
class Locator:

    mode: str = field(default="", compare=False)
    value: str = field(default="", compare=False)
    index: int = field(default=0, compare=False)
    uses: int = field(default=0, compare=True)

    @property
    def _mode(self) -> Mode:
        return Mode(self.mode)

    def __repr__(self) -> str:
        return f"<locator {self.mode}={self.value}>"

    def __bool__(self) -> bool:
        return bool(self.mode and self.value)

    def find(self) -> Optional[WebDriverElement]:
        elements = self._mode.finder(self.value)
        try:
            element = elements[self.index]
        except ElementDoesNotExist:
            log.debug(f"{self} unable to find element")
            return None
        else:
            log.debug(f"{self} found element: {element}")
            return element

    def score(self, value: int):
        previous = self.uses
        if value > 0:
            self.uses = min(99, max(1, self.uses + value))
        else:
            self.uses = max(-1, self.uses + value)
        if self.uses > previous:
            log.debug(f"Increased {self} uses to {self.uses}")
        elif self.uses < previous:
            log.debug(f"Decreased {self} uses to {self.uses}")


@datafile
class Action:

    verb: str = ""
    name: str = ""
    locators: List[Locator] = field(default_factory=lambda: [Locator()])

    @property
    def locators_sorted(self) -> List[Locator]:
        return [x for x in sorted(self.locators, reverse=True) if x]

    @property
    def _verb(self) -> Verb:
        return Verb(self.verb)

    def __post_init__(self):
        if self.verb and len(self.locators) <= 1:
            for mode, value in self._verb.get_default_locators(self.name):
                self.locators.append(Locator(mode, value))

    def __str__(self):
        return f"{self.verb}_{self.name}"

    def __bool__(self) -> bool:
        return bool(self.verb and self.name)

    def __call__(self, *args, **kwargs) -> "Page":
        page = kwargs.pop("_page", None)
        locator = kwargs.pop("_locator", "")

        if "=" in locator:
            mode, value = locator.split("=", 1)
            self.locators.insert(0, Locator(mode, value))
            self.datafile.save()

        page = self._call_method(page, locator, *args, **kwargs)
        self.datafile.save()
        page.clean()

        return page

    def _call_method(self, page, locator, *args, **kwargs) -> "Page":
        while self._finding_locator(*args, **kwargs):
            log.error(f"No locators able to find {self.name!r}")

            if locator or not shared.cli:
                break

            choices = ["<cancel>"] + [mode.value for mode in Mode]
            command = shared.cli.Bullet(
                prompt="\nSelect element locator: ",
                bullet=" ● ",
                choices=choices,
            )
            mode = command.launch()
            if mode == "<cancel>":
                print()
                break

            command = shared.cli.Input("\nValue to match: ")
            value = command.launch()
            print()

            self.locators.append(Locator(mode, value))

        if page and self._verb.updates:
            return page

        return autopage()

    def _finding_locator(self, *args, **kwargs) -> bool:
        for locator in self.locators_sorted:
            if locator:
                log.debug(f"Using {locator} to find {self.name!r}")
                element = locator.find()
                if element:
                    if self._perform_action(element, *args, **kwargs):
                        locator.score(+1)
                        return False
            locator.score(-1)
        return True

    def _perform_action(self, element: WebDriverElement, *args, **kwargs) -> bool:
        delay = kwargs.pop("delay", 0.0)
        function = getattr(element, self.verb)
        try:
            function(*args, **kwargs)
        except WebDriverException as e:
            log.debug(e)
            return False
        else:
            self._verb.post_action(delay=delay)
            return True

    def clean(self, *, force: bool = False) -> int:
        unused_locators = []
        remove_unused_locators = force

        for locator in self.locators:
            if locator.uses <= 0:
                unused_locators.append(locator)
            if locator.uses >= 99:
                remove_unused_locators = True

        log.debug(f"Found {len(unused_locators)} unused locators for {self}")
        if not remove_unused_locators:
            return 0

        if unused_locators:
            log.info(f"Cleaning up locators for {self}")
            for locator in unused_locators:
                log.info(f"Removed unused {locator}")
                self.locators.remove(locator)

        return len(unused_locators)


@datafile(
    "./sites/{self.domain}/{self.path}/{self.variant}.yml", defaults=True, manual=True
)
class Page:

    domain: str
    path: str = URL.ROOT
    variant: str = "default"

    active_locators: List[Locator] = field(default_factory=lambda: [Locator()])
    inactive_locators: List[Locator] = field(default_factory=lambda: [Locator()])

    actions: List[Action] = field(default_factory=lambda: [Action()])

    @classmethod
    def at(cls, url: str, *, variant: str = "") -> "Page":
        if shared.browser.url != url:
            log.info(f"Visiting {url}")
            shared.browser.visit(url)

        if shared.browser.url != url:
            log.info(f"Redirected to {url}")

        kwargs = {"domain": URL(url).domain, "path": URL(url).path}
        variant = variant or URL(url).fragment
        if variant:
            kwargs["variant"] = variant

        return cls(**kwargs)  # type: ignore

    @property
    def url(self) -> URL:
        return URL(self.domain, self.path)

    @property
    def active(self) -> bool:
        log.debug(f"Determining if {self!r} is active")

        if self.url != URL(shared.browser.url):
            log.debug(
                f"{self!r} is inactive - URL does not match: {shared.browser.url}"
            )
            return False

        log.debug("Checking that all expected elements can be found")
        for locator in self.active_locators:
            if locator and not locator.find():
                log.debug(f"{self!r} is inactive - Unable to find: {locator!r}")
                return False

        log.debug("Checking that no unexpected elements can be found")
        for locator in self.inactive_locators:
            if locator and locator.find():
                log.debug(f"{self!r} is inactive - Found unexpected: {locator!r}")
                return False

        log.debug(f"{self!r} is active")
        return True

    @property
    def text(self) -> str:
        return shared.browser.html

    @property
    def html(self) -> BeautifulSoup:
        return BeautifulSoup(self.text, "html.parser")

    def __repr__(self):
        if self.variant == "default":
            return f"Page.at('{self.url.value}')"
        return f"Page.at('{self.url.value}', variant='{self.variant}')"

    def __str__(self):
        if self.variant == "default":
            return f"{self.url}"
        return f"{self.url} ({self.variant})"

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

    def __getattr__(self, value: str) -> Action:
        if "_" in value:
            verb, name = value.split("_", 1)

            with suppress(FileNotFoundError):
                self.datafile.load()

            for action in self.actions:
                if action.name == name and action.verb == verb:
                    return action

            if Verb.validate(verb):
                action = Action(verb, name)
                setattr(
                    action, "datafile", mapper.create_mapper(action, root=self.datafile)
                )
                self.actions.append(action)
                return action

        return object.__getattribute__(self, value)

    def __contains__(self, value):
        return value in self.text

    def perform(self, name: str, *, prompt: Callable) -> Tuple["Page", bool]:
        action = getattr(self, name)
        if action.verb in {"fill", "select"}:
            value = settings.get_secret(action.name) or prompt()
            settings.update_secret(action.name, value)
            page = action(value, _page=self)
        else:
            page = action(_page=self)
        return page, page != self

    def clean(self, *, force: bool = False) -> int:
        count = 0

        unused_actions = []
        remove_unused_actions = force

        for action in self.actions:
            if all(locator.uses <= 0 for locator in action.locators):
                unused_actions.append(action)

        log.debug(f"Found {len(unused_actions)} unused actions for {self}")
        if unused_actions and remove_unused_actions:
            log.info(f"Cleaning up actions for {self}")
            for action in unused_actions:
                log.info(f"Removed unused {action}")
                self.actions.remove(action)

        for action in self.actions:
            count += action.clean(force=force)

        if count:
            self.datafile.save()

        return count


def autopage() -> Page:
    matching_pages = []

    for page in Page.objects.filter(domain=URL(shared.browser.url).domain):
        if page.active:
            matching_pages.append(page)

    if matching_pages:
        if len(matching_pages) > 1:
            for page in matching_pages:
                log.warn(f"Multiple pages matched: {page}")
        return matching_pages[0]

    log.info(f"Creating new page: {shared.browser.url}")
    page = Page.at(shared.browser.url)
    page.datafile.save()
    return page
