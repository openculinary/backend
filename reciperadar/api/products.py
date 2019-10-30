from ipaddress import ip_address

from flask import abort, jsonify, request

from reciperadar import app
from reciperadar.search.products import ProductSearch


@app.route('/api/products')
def products():
    forwarded_for = request.headers.get('x-forwarded-for')
    if forwarded_for and not ip_address(forwarded_for).is_private:
        return abort(403)

    products = ProductSearch().products()
    return jsonify(products)
