from pkg_resources import DistributionNotFound, get_distribution

from .api import prompt, visit


try:
    __version__ = get_distribution('pomace').version
except DistributionNotFound:
    __version__ = '(local)'
