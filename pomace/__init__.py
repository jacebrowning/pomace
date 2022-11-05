from importlib.metadata import PackageNotFoundError, version

from .api import *
from .config import settings

try:
    __version__ = version("pomace")
except PackageNotFoundError:
    __version__ = "(local)"

del PackageNotFoundError
del version
