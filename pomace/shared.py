import log
from splinter import Browser


try:
    import bullet as cli  # pylint: disable=unused-import
except ImportError:
    cli = None  # https://github.com/Mckinsey666/bullet/issues/2
    log.warn("Interactive CLI prompts not yet supported on Windows")

browser: Browser = None
