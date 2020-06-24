import json

from flask import Response

from reciperadar import app
from reciperadar.search.products import ProductSearch


# Custom streaming method
def stream(items):
    for item in items:
        line = json.dumps(item, ensure_ascii=False)
        yield f'{line}\n'


@app.route('/api/products')
def products():
    products = ProductSearch().products()
    return Response(stream(products), content_type='application/x-ndjson')
