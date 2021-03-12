from flask import redirect, request
from flask_api import FlaskAPI

from . import models


app = FlaskAPI("Pomace")


@app.route("/")
def index():
    page = models.auto()
    return redirect("/" + page.domain)


@app.route("/favicon.ico")
def favicon():
    return ("", 204)


@app.route("/<path:domain>")
def pomace(domain: str):
    url = "https://" + domain
    page = models.Page.at(url)

    for action, value in request.args.items():
        page, _updated = page.perform(action, value, _logger=app.logger)

    if request.args:
        domain = page.url.value.split("://", 1)[-1]
        return redirect("/" + domain)

    return {
        "page": str(page),
        "actions": [str(a) for a in page.actions if a],
        "html": page.text,
    }
