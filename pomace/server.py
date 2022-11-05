from urllib.parse import unquote

import log
from flask import redirect, request, url_for
from flask_api import FlaskAPI

from .api import visit

app = FlaskAPI("Pomace")


@app.route("/")
def index():
    return redirect("/sites?url=http://example.com")


@app.route("/sites")
def pomace():
    if "url" not in request.args:
        return redirect("/")

    url = request.args["url"]
    page = visit(url)

    transitioned = False
    for action, value in request.args.items():
        if "_" in action:
            page, transitioned = page.perform(action, value or "<missing>")
            if transitioned:
                log.info(f"Transitioned to {page}")

    link = unquote(url_for(".pomace", url=page.url, _external=True))
    if transitioned:
        return redirect(link)

    data = {
        "id": page.identity,
        "url": page.url,
        "title": page.title,
        "html": page.soup.prettify(),
        "text": page.text,
        "_self": link,
        "_actions": {action: link + "&" + action for action in dir(page)},
    }

    return data
