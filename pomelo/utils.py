from urllib.parse import urlparse

import log

from . import shared
from .models import Page


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
