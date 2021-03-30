from contextlib import suppress
from copy import copy
from typing import Callable, List, Optional, Tuple

import log
from bs4 import BeautifulSoup
from cached_property import cached_property
from datafiles import datafile, field, mapper
from selenium.common.exceptions import (
    ElementNotInteractableException,
    WebDriverException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from splinter import Browser
from splinter.driver.webdriver import WebDriverElement
from splinter.exceptions import ElementDoesNotExist

from . import prompts, shared
from .config import settings
from .enums import Mode, Verb
from .types import URL


__all__ = ["Locator", "Action", "Page", "auto"]


@datafile(order=True)
class Locator:

    mode: str = field(default="", compare=False)
    value: str = field(default="", compare=False)
    index: int = field(default=0, compare=False)
    uses: int = field(default=0, compare=True)

    def __repr__(self) -> str:
        return f"<locator {self.mode}={self.value}[{self.index}]>"

    def __bool__(self) -> bool:
        return bool(self.mode and self.value)

    def find(self) -> Optional[WebDriverElement]:
        elements = self._mode.find(self.value)
        index = self.index
        try:
            element = elements[index]
            if index == 0 and not element.visible:
                log.debug(f"{self} found invisible element: {element.outer_html}")
                index += 1
                element = elements[index]
        except ElementDoesNotExist:
            log.debug(f"{self} unable to find element")
            return None
        else:
            self.index = index
            log.debug(f"{self} found element: {element.outer_html}")
            return element

    def score(self, value: int) -> bool:
        previous = self.uses

        if value > 0:
            self.uses = min(99, max(1, self.uses + value))
        else:
            self.uses = max(-1, self.uses + value)

        if self.uses == previous:
            return False

        result = "Increased" if self.uses > previous else "Decreased"
        log.debug(f"{result} {self} uses to {self.uses}")
        return True

    @property
    def _mode(self) -> Mode:
        return Mode(self.mode)


@datafile
class Action:

    verb: str = ""
    name: str = ""
    locators: List[Locator] = field(default_factory=lambda: [Locator()])

    @property
    def humanized(self) -> str:
        return self._verb.humanized + " " + self.name.replace("_", " ")

    @property
    def sorted_locators(self) -> List[Locator]:
        return [x for x in sorted(self.locators, reverse=True) if x]

    @property
    def locator(self) -> Locator:
        try:
            return self.sorted_locators[0]
        except IndexError:
            return Locator("id", "placeholder")

    @property
    def valid(self) -> bool:
        return self.locator.uses >= 0

    def __post_init__(self):
        if self.verb and self._verb != Verb.TYPE and not self.sorted_locators:
            if settings.dev:
                log.info(f"Adding placeholder locators for {self}")
                for mode, value in self._verb.get_default_locators(self.name):
                    self.locators.append(Locator(mode, value))
            else:
                log.debug("Placeholder locators are disabled")

    def __str__(self):
        return f"{self.verb}_{self.name}"

    def __bool__(self) -> bool:
        return bool(self.verb and self.name)

    def __call__(self, *args, **kwargs) -> "Page":
        page = kwargs.pop("_page", None)
        page = self._call_method(page, *args, **kwargs)
        self.datafile.save()
        page.clean()
        return page

    def _call_method(self, page, *args, **kwargs) -> "Page":
        while self._trying_locators(*args, **kwargs):
            log.error(f"No locators able to find {self.name!r}")
            if prompts.bullet:
                shared.linebreak = False
            mode, value = prompts.mode_and_value()
            if mode and value:
                self.locators.append(Locator(mode, value))
            else:
                break

        if page and self._verb.updates:
            return page

        return auto()

    def _trying_locators(self, *args, **kwargs) -> bool:
        if self._verb == Verb.TYPE:
            if "_" in self.name:
                names = self.name.split("_")
                assert len(names) == 2, "Multiple modifier keys not supported"
                modifier = getattr(Keys, names[0].upper())
                key = getattr(Keys, names[-1].upper())
                function = (
                    ActionChains(shared.browser.driver)
                    .key_down(modifier)
                    .send_keys(key)
                    .key_up(modifier)
                    .perform
                )
            else:
                key = getattr(Keys, self.name.upper())
                function = ActionChains(shared.browser.driver).send_keys(key).perform
            self._perform_action(function, *args, **kwargs)
            return False

        for locator in self.sorted_locators:
            if locator:
                log.debug(f"Using {locator} to find {self.name!r}")
                element = locator.find()
                if element:
                    function = getattr(element, self.verb)
                    if self._perform_action(function, *args, **kwargs):
                        locator.score(+1)
                        return False
            locator.score(-1)

        return True

    def _perform_action(self, function: Callable, *args, **kwargs) -> bool:
        previous_url = shared.browser.url
        delay = kwargs.pop("delay", None)
        wait = kwargs.pop("wait", None)
        self._verb.pre_action()
        try:
            function(*args, **kwargs)
        except ElementDoesNotExist as e:
            log.warn(e)
            return False
        except ElementNotInteractableException as e:
            log.warn(e.msg)
            return False
        except WebDriverException as e:
            log.debug(e)
            return False
        else:
            self._verb.post_action(previous_url, delay, wait)
            return True

    def clean(self, page, *, force: bool = False) -> int:
        unused_locators = []
        remove_unused_locators = force

        for locator in self.locators:
            if locator.uses <= 0:
                unused_locators.append(locator)
            if locator.uses >= 99:
                remove_unused_locators = True

        log.debug(f"Found {len(unused_locators)} unused locators for {self} on {page}")
        if not remove_unused_locators:
            return 0

        if unused_locators:
            log.info(f"Cleaning up locators for {self} on {page}")
            for locator in unused_locators:
                log.info(f"Removed unused {locator}")
                self.locators.remove(locator)

        return len(unused_locators)

    @property
    def _verb(self) -> Verb:
        return Verb(self.verb)


@datafile
class Locators:
    inclusions: List[Locator] = field(default_factory=lambda: [Locator()])
    exclusions: List[Locator] = field(default_factory=lambda: [Locator()])

    @property
    def sorted_inclusions(self) -> List[Locator]:
        return [x for x in sorted(self.inclusions, reverse=True) if x]

    @property
    def sorted_exclusions(self) -> List[Locator]:
        return [x for x in sorted(self.exclusions, reverse=True) if x]

    def clean(self, page, *, force: bool = False) -> int:
        unused_inclusion_locators = []
        unused_exclusion_locators = []
        remove_unused_locators = force

        for locator in self.inclusions:
            if locator.uses <= 0:
                unused_inclusion_locators.append(locator)
            if locator.uses >= 99:
                remove_unused_locators = True

        for locator in self.exclusions:
            if locator.uses <= 0:
                unused_exclusion_locators.append(locator)
            if locator.uses >= 99:
                remove_unused_locators = True

        count = len(unused_inclusion_locators) + len(unused_exclusion_locators)
        log.debug(f"Found {count} unused locators for {page}")
        if not remove_unused_locators:
            return 0

        if unused_inclusion_locators:
            log.info(f"Cleaning up inclusion locators for {page}")
            for locator in unused_inclusion_locators:
                log.info(f"Removed unused {locator}")
                self.inclusions.remove(locator)

        if unused_exclusion_locators:
            log.info(f"Cleaning up exclusion locators for {page}")
            for locator in unused_exclusion_locators:
                log.info(f"Removed unused {locator}")
                self.exclusions.remove(locator)

        return len(unused_inclusion_locators) + len(unused_exclusion_locators)


@datafile(
    "./sites/{self.domain}/{self.path}/{self.variant}.yml", defaults=True, manual=True
)
class Page:

    domain: str
    path: str = URL.ROOT
    variant: str = "default"

    locators: Locators = field(default_factory=Locators)
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

        page = cls(**kwargs)  # type: ignore
        log.debug(f"Loaded {page.url}: {page.title} ({page.identity})")
        return page

    @property
    def url_pattern(self) -> URL:
        return URL(self.domain, self.path)

    @property
    def exact(self) -> bool:
        return "{" not in self.path

    @property
    def browser(self) -> Browser:
        return shared.browser

    @cached_property
    def url(self) -> str:
        return self.browser.url

    @cached_property
    def title(self) -> str:
        return self.browser.title

    @cached_property
    def identity(self) -> int:
        return sum(ord(c) for c in self.text)

    @cached_property
    def text(self) -> str:
        html = copy(self.html)
        for element in html(["script", "style"]):
            element.extract()
        lines = (line.strip() for line in html.get_text().splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)

    @cached_property
    def html(self) -> BeautifulSoup:
        return BeautifulSoup(self.browser.html, "html.parser")

    @property
    def active(self) -> bool:
        log.debug(f"Determining if {self!r} is active")

        if self.url_pattern != URL(shared.browser.url):
            log.debug(f"{self!r} is inactive: URL not matched")
            return False

        log.debug("Checking that all expected elements can be found")
        for locator in self.locators.sorted_inclusions:
            if locator.find():
                if locator.score(+1):
                    self.datafile.save()
            else:
                log.debug(f"{self!r} is inactive: {locator!r} found expected element")
                return False

        log.debug("Checking that no unexpected elements can be found")
        for locator in self.locators.sorted_exclusions:
            if locator.find():
                if locator.score(+1):
                    self.datafile.save()
                log.debug(f"{self!r} is inactive: {locator!r} found unexpected element")
                return False

        log.debug(f"{self!r} is active")
        return True

    def __repr__(self):
        if self.variant == "default":
            return f"Page.at('{self.url_pattern}')"
        return f"Page.at('{self.url_pattern}', variant='{self.variant}')"

    def __str__(self):
        if self.variant == "default":
            return f"{self.url_pattern}"
        return f"{self.url_pattern} ({self.variant})"

    def __dir__(self):
        names = []
        add_placeholder = True
        for action in self.actions:
            if action:
                if action.valid:
                    names.append(str(action))
            else:
                add_placeholder = False
        if add_placeholder:
            if settings.dev:
                log.info(f"Adding placeholder action for {self}")
                self.actions.append(Action())
            else:
                log.debug("Placeholder actions are disabled")
        return names

    def __getattr__(self, value: str) -> Action:
        if "_" in value:
            verb, name = value.split("_", 1)

            with suppress(FileNotFoundError):
                self.datafile.load()

            for action in self.actions:
                if action.name == name and action.verb == verb:
                    return action

            if Verb.validate(verb, name):
                action = Action(verb, name)
                setattr(
                    action,
                    "datafile",
                    mapper.create_mapper(action, root=self.datafile),
                )
                if settings.dev:
                    self.actions.append(action)
                else:
                    log.debug("Automatic actions are disabled")
                return action

        return object.__getattribute__(self, value)

    def __contains__(self, value):
        return value in self.text

    def perform(self, name: str, value: str = "", _logger=None) -> Tuple["Page", bool]:
        _logger = _logger or log
        action = getattr(self, name)
        if action.verb in {"fill", "select"}:
            if not value:
                value = settings.get_secret(action.name) or prompts.named_value(
                    action.name
                )
                settings.update_secret(action.name, value)
            _logger.info(f"{action.humanized} with {value!r}")
            page = action(value, _page=self)
        else:
            _logger.info(f"{action.humanized}")
            page = action(_page=self)
        return page, page != self

    def clean(self, *, force: bool = False) -> int:
        count = self.locators.clean(self, force=force)

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
            count += action.clean(self, force=force)

        if count or force:
            self.datafile.save()

        return count


def auto() -> Page:
    matching_pages = []
    found_exact_match = False

    for page in Page.objects.filter(domain=URL(shared.browser.url).domain):
        if page.active:
            matching_pages.append(page)
            if page.exact:
                found_exact_match = True

    if found_exact_match:
        log.debug("Removing abstract pages from matches")
        matching_pages = [page for page in matching_pages if page.exact]

    if matching_pages:
        if len(matching_pages) > 1:
            for page in matching_pages:
                log.warn(f"Multiple pages matched: {page}")
                if prompts.bullet:
                    shared.linebreak = False
        return matching_pages[0]

    log.info(f"Creating new page: {shared.browser.url}")
    page = Page.at(shared.browser.url)
    page.datafile.save()
    return page
