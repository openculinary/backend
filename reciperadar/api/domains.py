from flask import abort, jsonify

from reciperadar import app
from reciperadar.models.domain import Domain


@app.route('/domains/<domain>')
def domain_get(domain):
    domain = Domain.query.get(domain)
    if not domain:
        return abort(404)
    return jsonify(domain.to_doc())
