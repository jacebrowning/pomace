from urllib.parse import unquote

from flask import redirect, request, url_for
from flask_api import FlaskAPI

from . import models, utils

app = FlaskAPI("Pomace")


@app.route("/")
def index():
    return redirect("/sites?url=http://example.com")


@app.route("/sites")
def pomace():
    if "url" not in request.args:
        return redirect("/")

    utils.launch_browser(restore_previous_url=False)

    url = request.args["url"]
    page = models.Page.at(url)

    for action, value in request.args.items():
        if "_" in action:
            page, _updated = page.perform(action, value, _log=app.logger)

    data = {
        "id": page.identity,
        "url": page.url,
        "title": page.title,
        "html": page.soup.prettify(),
        "text": page.text,
        "_next": unquote(url_for(".pomace", url=page.url, _external=True)),
        "_actions": dir(page),
    }

    if not app.debug:
        utils.close_browser()

    return data
