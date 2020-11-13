import argparse
import json
import requests

from reciperadar import db
from reciperadar.models.recipes.product import Product

parser = argparse.ArgumentParser(description='Load product hierarchy')
parser.add_argument('--filename', required=True)
args = parser.parse_args()

db.session.query(Product).delete()
with open(args.filename, 'r') as f:
    for line in f.readlines():
        if line.startswith('#'):
            continue
        doc = json.loads(line)
        product = Product.from_doc(doc)
        try:
            product_info = requests.get(
                url=f'http://localhost:30080/products/{product.id}',
                headers={'Host': 'knowledge-graph'},
            ).json()
        except Exception:
            continue

        product.product = product_info['product']
        product.singular = product_info['singular']
        product.plural = product_info['plural']
        product.category = product_info['category']
        product.is_dairy_free = product_info['is_dairy_free']
        product.is_gluten_free = product_info['is_gluten_free']
        product.is_vegan = product_info['is_vegan']
        product.is_vegetarian = product_info['is_vegetarian']
        product.is_kitchen_staple = product_info['is_kitchen_staple']

        db.session.add(product)
db.session.commit()
