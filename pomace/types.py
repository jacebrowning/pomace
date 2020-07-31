from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from parse import parse


class URL:

    ROOT = '@'

    def __init__(self, url_or_domain: str, path: Optional[str] = None):
        if path == self.ROOT:
            self.value = f'https://{url_or_domain}'
        elif path:
            path = ('/' + path).rstrip('/').replace('//', '/')
            self.value = f'https://{url_or_domain}' + path
        else:
            self.value = str(url_or_domain).rstrip('/')

    def __repr__(self):
        return f"URL({self.value!r})"

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

    def __contains__(self, value):
        return value in self.value

    @property
    def domain(self) -> str:
        return urlparse(self.value).netloc

    @property
    def path(self) -> str:
        path = urlparse(self.value).path.strip('/')
        return path if path else self.ROOT

    @property
    def fragment(self) -> str:
        return urlparse(self.value).fragment.replace('/', '_').strip('_')


@dataclass
class Person:
    honorific: str
    first_name: str
    last_name: str
    email_address: str
    zip_code: str

    @property
    def prefix(self) -> str:
        return self.honorific

    @property
    def email(self) -> str:
        return self.email_address

    @property
    def zip(self) -> str:
        return self.zip_code
