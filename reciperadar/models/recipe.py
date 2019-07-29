from base58 import b58encode
from bs4 import BeautifulSoup
import mmh3
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import tldextract
from urltools import normalize

from reciperadar.models.base import Searchable, Storable


class RecipeIngredient(Storable):
    __tablename__ = 'recipe_ingredients'

    fk = ForeignKey('recipes.id', ondelete='cascade')
    recipe_id = Column(String, fk, primary_key=True)
    id = Column(String, primary_key=True)
    ingredient = Column(String)

    product = Column(String)
    quantity = Column(Float)
    units = Column(String)
    verb = Column(String)

    @staticmethod
    def from_doc(doc):
        ingredient = doc['ingredient'].strip()
        product = doc.get('product')
        quantity = doc.get('quantity')
        units = doc.get('units')
        verb = doc.get('verb')
        id_string = '{}/{}'.format(ingredient, verb or 'undefined')

        ingredient_id = b58encode(mmh3.hash_bytes(id_string)).decode('utf-8')
        return RecipeIngredient(
            id=ingredient_id,
            ingredient=ingredient,
            product=product,
            quantity=quantity,
            units=units,
            verb=verb
        )

    def generate_update_script(self):
        return {
            'lang': 'painless',
            'source': '''
              for (int i = 0; i < ctx._source.ingredients.size(); i++) {
                if (ctx._source.ingredients[i].id == params.ingredient_id) {
                  ctx._source.ingredients[i].product = params.product;
                  ctx._source.ingredients[i].quantity = params.quantity;
                  ctx._source.ingredients[i].units = params.units;
                  ctx._source.ingredients[i].verb = params.verb;
                  break;
                }
              }''',
            'params': {
                'ingredient_id': self.id,
                'product': self.product,
                'quantity': self.quantity,
                'units': self.units,
                'verb': self.verb,
            }
        }


class Recipe(Storable, Searchable):
    __tablename__ = 'recipes'

    id = Column(String, primary_key=True)
    title = Column(String)
    url = Column(String)
    image = Column(String)
    time = Column(Integer)
    servings = Column(Integer)
    ingredients = relationship(
        'RecipeIngredient',
        backref='recipe',
        passive_deletes='all'
    )

    @property
    def noun(self):
        return 'recipes'

    @staticmethod
    def from_dict(data):
        url = normalize(data['url'])
        recipe_id = b58encode(mmh3.hash_bytes(url)).decode('utf-8')

        # Parse and de-duplicate ingredients
        ingredients = [
            RecipeIngredient.from_doc(ingredient)
            for ingredient in data['ingredients']
            if ingredient['ingredient'].strip()
        ]
        ingredients = {
            ingredient.id: ingredient
            for ingredient in ingredients
        }

        return Recipe(
            id=recipe_id,
            title=data['title'],
            url=url,
            image=data.get('image'),
            ingredients=list(ingredients.values()),
            servings=data['servings'],
            time=data['time'],
        )

    def generate_action_metadata(self):
        return {
            '_index': self.noun,
            '_type': '_doc',
            '_id': self.id
        }

    def index(self):
        items = []
        items.append({'index': self.generate_action_metadata()})
        items.append(self.to_dict())
        for ingredient in self.ingredients:
            items.append({'update': self.generate_action_metadata()})
            items.append({'script': ingredient.generate_update_script()})
        self.es.bulk(items)

    @staticmethod
    def matches(doc, includes):
        matches = []
        highlights = []
        for item in doc.get('inner_hits', {}).values():
            for hit in item['hits']['hits']:
                highlights += hit.get('highlight', {}) \
                              .get('ingredients.product', [])
        for highlight in highlights:
            bs = BeautifulSoup(highlight, features='html.parser')
            matches += [em.text.lower() for em in bs.findAll('em')]
        return {'matches': [inc for inc in includes if inc in matches]}

    @staticmethod
    def from_doc(doc):
        source = doc.pop('_source')
        return Recipe(
            id=doc['_id'],
            title=source['title'],
            url=source['url'],
            image=source['image'],
            ingredients=[
                RecipeIngredient.from_doc(ingredient)
                for ingredient in source['ingredients']
                if ingredient['ingredient'].strip()
            ],
            servings=source.get('servings'),
            time=source['time']
        )

    def to_dict(self):
        url_info = tldextract.extract(self.url)

        data = super().to_dict()
        data['ingredients'] = [
            ingredient.to_dict()
            for ingredient in self.ingredients
        ]
        data['domain'] = '{}.{}'.format(url_info.domain, url_info.suffix)
        return data

    @staticmethod
    def _generate_should_clause(include):
        highlight = {'type': 'fvh', 'fields': {'ingredients.product': {}}}
        return [{
            'nested': {
                'path': 'ingredients',
                'query': {
                    'constant_score': {
                        'boost': 1.0 / idx,
                        'filter': {
                            'match_phrase': {'ingredients.product': inc}
                        }
                    }
                },
                'inner_hits': {'highlight': highlight, 'name': inc},
                'score_mode': 'max'
            }
        } for idx, inc in enumerate(include, start=1)]

    @staticmethod
    def _generate_must_not_clause(include, exclude):
        return [{
            'nested': {
                'path': 'ingredients',
                'query': {
                    'match_phrase': {
                        'ingredients.ingredient': {
                            'query': '{} stock'.format(inc),
                            'slop': 3
                        }
                    }
                }
            }
        } for inc in include] + [{
            'nested': {
                'path': 'ingredients',
                'query': {'match_phrase': {'ingredients.product': exc}}
            }
        } for exc in exclude]

    def search(self, include, exclude, offset, limit):
        offset = max(0, offset)
        limit = max(1, limit)
        limit = min(25, limit)

        should_clause = self._generate_should_clause(include)
        must_not_clause = self._generate_must_not_clause(include, exclude)

        results = self.es.search(
            index=self.noun,
            body={
                'from': offset,
                'size': limit,
                'query': {
                    'bool': {
                        'should': should_clause,
                        'must_not': must_not_clause,
                        'filter': [
                            {'range': {'time': {'gte': 5}}},
                            {'wildcard': {'image': '*'}},
                        ],
                        'minimum_should_match': 1 if should_clause else 0
                    }
                }
            }
        )

        return {
            'total': min(results['hits']['total']['value'], 50 * limit),
            'results': [
                {
                    **self.from_doc(result).to_dict(),
                    **self.matches(result, include)
                }
                for result in results['hits']['hits']
            ]
        }
