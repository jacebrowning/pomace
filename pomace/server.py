from flask import redirect, request
from flask_api import FlaskAPI

from . import models, utils


app = FlaskAPI("Pomace")


@app.route("/")
def index():
    return redirect("/sites/example.com")


@app.route("/sites/<path:domain>")
def pomace(domain: str):
    utils.launch_browser()

    url = "https://" + domain
    page = models.Page.at(url)

    for action, value in request.args.items():
        page, _updated = page.perform(action, value, _logger=app.logger)

    if request.args:
        domain = page.url.value.split("://", 1)[-1]
        return redirect("/sites/" + domain)

    data = {
        "page": str(page),
        "actions": [str(a) for a in page.actions if a],
        "html": page.text,
    }

    if not app.debug:
        utils.quit_browser()

    return data
