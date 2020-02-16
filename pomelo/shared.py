import datafiles
from splinter import Browser


datafiles.settings.YAML_LIBRARY = 'PyYAML'

browser: Browser = None
