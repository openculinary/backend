from flask import abort, jsonify

from reciperadar import app, db
from reciperadar.models.domain import Domain


@app.route("/domains/<domain>")
def domain_get(domain):
    domain = db.session.get(Domain, domain)
    if not domain:
        return abort(404)
    return jsonify(domain.to_doc())
