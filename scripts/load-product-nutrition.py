import argparse
import json
import requests

from reciperadar import db
from reciperadar.models.recipes.nutrition import ProductNutrition

parser = argparse.ArgumentParser(description='Load product nutrition')
parser.add_argument('--filename', required=True)
args = parser.parse_args()

db.session.query(ProductNutrition).delete()
with open(args.filename, 'r') as f:
    for line in f.readlines():
        if line.startswith('#'):
            continue
        doc = json.loads(line)
        product_id = doc.get('id')
        try:
            product_info = requests.get(
                url=f'http://localhost:30080/products/{product_id}',
                headers={'Host': 'knowledge-graph'},
            ).json()
        except Exception:
            continue

        nutrition = product_info.get('nutrition')
        if not nutrition:
            continue

        nutrition = ProductNutrition.from_doc(nutrition)
        nutrition.product_id = product_id

        db.session.add(nutrition)
db.session.commit()
