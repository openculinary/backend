from flask import jsonify

from reciperadar import app, db
from reciperadar.models.domain import Domain


@app.route("/domains/<domain>")
def domain_get(domain):
    domain = db.session.get_or_404(Domain, domain)
    return jsonify(domain.to_doc())
