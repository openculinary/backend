from flask import jsonify

from reciperadar import app
from reciperadar.search.products import ProductSearch
from reciperadar.utils.decorators import internal


@app.route('/api/products')
@internal
def products():
    products = ProductSearch().products()
    return jsonify(products)
