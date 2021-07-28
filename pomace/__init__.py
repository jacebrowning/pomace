from pkg_resources import (
    DistributionNotFound as _DistributionNotFound,
    get_distribution as _get_distribution,
)

from .api import *
from .config import settings


try:
    __version__ = _get_distribution("pomace").version
except _DistributionNotFound:
    __version__ = "(local)"
