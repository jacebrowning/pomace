from . import shared
from .models import Page


def autopage() -> Page:
    page = Page.at(shared.browser.url)
    page.datafile.save()  # type: ignore
    return page
