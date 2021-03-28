import atexit
import inspect
import os
import time
from pathlib import Path

import log
from gitman.decorators import preserve_cwd
from gitman.models import Source
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import HTTPError

from . import browser, shared
from .config import settings


def launch_browser(
    delay: float = 0.0,
    *,
    silence_logging: bool = False,
    restore_previous_url: bool = True,
) -> bool:
    did_launch = False

    if silence_logging:
        log.silence("urllib3.connectionpool")

    if shared.browser:
        try:
            log.debug(f"Current browser windows: {shared.browser.windows}")
            log.debug(f"Current browser URL: {shared.browser.url}")
        except (WebDriverException, HTTPError) as e:
            log.warn(str(e).strip())
            shared.browser = None

    if not shared.browser:
        shared.browser = browser.launch()
        atexit.register(quit_browser, silence_logging=silence_logging)
        browser.resize(shared.browser)
        did_launch = True

    if restore_previous_url and settings.url:
        shared.browser.visit(settings.url)
        time.sleep(delay)

    return did_launch


def quit_browser(*, silence_logging: bool = False) -> bool:
    did_quit = False

    if silence_logging:
        log.silence("pomace", "selenium", allow_warning=True)

    if shared.browser:
        try:
            browser.save_url(shared.browser)
            browser.save_size(shared.browser)
            shared.browser.quit()
        except Exception as e:
            log.debug(e)
        else:
            did_quit = True
        shared.browser = None

    path = Path().resolve()
    for _ in range(5):
        logfile = path / "geckodriver.log"
        if logfile.exists():
            log.debug(f"Deleting {logfile}")
            logfile.unlink()
        path = path.parent

    return did_quit


def locate_models(*, caller=None):
    cwd = Path.cwd()

    if caller:
        for frame in inspect.getouterframes(caller):
            if "pomace" not in frame.filename or "pomace/tests" in frame.filename:
                path = Path(frame.filename)
                log.debug(f"Found caller's package directory: {path.parent}")
                os.chdir(path.parent)
                return

    if (cwd / "sites").is_dir():
        log.debug(f"Found models in current directory: {cwd}")
        return

    for path in cwd.iterdir():
        if (path / "sites").is_dir():
            log.debug(f"Found models in package directory: {path}")
            os.chdir(path)
            return


@preserve_cwd
def clone_models(url: str, *, domain: str = "", force: bool = False):
    repository = url.replace(".git", "").split("/")[-1]
    domain = domain or repository.replace("pomace-", "")
    directory = Path("sites") / domain
    log.info(f"Cloning {url} to {directory}")
    assert "." in domain, f"Invalid domain: {domain}"
    source = Source(url, directory)
    source.update_files(force=force)
