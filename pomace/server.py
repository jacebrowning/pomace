from flask import redirect, request, url_for
from flask_api import FlaskAPI

from . import models, utils


app = FlaskAPI("Pomace")


@app.route("/")
def index():
    return redirect("/sites/example.com")


@app.route("/sites/<path:domain>")
def pomace(domain: str):
    utils.launch_browser(restore_previous_url=False)

    url = "https://" + domain
    page = models.Page.at(url)

    for action, value in request.args.items():
        page, _updated = page.perform(action, value, _logger=app.logger)

    domain = page.url.value.split("://", 1)[-1]
    data = {
        "id": sum(ord(c) for c in page.text),
        "url": str(page.url),
        "html": page.text,
        "_next": url_for(".pomace", domain=domain, _external=True),
        "_actions": [str(a) for a in page.actions if a],
    }

    if not app.debug:
        utils.quit_browser()

    return data
