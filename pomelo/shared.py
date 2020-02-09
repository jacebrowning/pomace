from splinter import Browser

import datafiles


datafiles.settings.YAML_LIBRARY = 'PyYAML'

browser: Browser = None
