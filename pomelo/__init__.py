from pkg_resources import DistributionNotFound, get_distribution

from .models import Page, autopage


try:
    __version__ = get_distribution('Pomelo').version
except DistributionNotFound:
    __version__ = '(local)'
