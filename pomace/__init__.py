from pkg_resources import DistributionNotFound, get_distribution

from .api import visit
from .config import settings
from .models import Page, autopage


try:
    __version__ = get_distribution('pomace').version
except DistributionNotFound:
    __version__ = '(local)'
