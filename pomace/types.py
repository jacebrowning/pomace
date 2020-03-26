from urllib.parse import urlparse

from parse import parse


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
