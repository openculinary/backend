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

    @staticmethod
    def from_ingredient(ingredient):
        ingredient_id = b58encode(mmh3.hash_bytes(ingredient)).decode('utf-8')
        return RecipeIngredient(
            id=ingredient_id,
            ingredient=ingredient
        )

    @staticmethod
    def from_doc(doc):
        ingredient = doc['ingredient']
        ingredient_id = b58encode(mmh3.hash_bytes(ingredient)).decode('utf-8')
        return RecipeIngredient(
            id=ingredient_id,
            ingredient=ingredient
        )


class Recipe(Storable, Searchable):
    __tablename__ = 'recipes'

    id = Column(String, primary_key=True)
    title = Column(String)
    url = Column(String)
    image = Column(String)
    time = Column(Integer)
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

        return Recipe(
            id=recipe_id,
            title=data['title'],
            url=url,
            image=data.get('image'),
            ingredients=[
                RecipeIngredient.from_ingredient(ingredient)
                for ingredient in set(data['ingredients'])
                if ingredient.strip()
            ],
            time=data['time'],
        )

    @staticmethod
    def matches(doc):
        matches = []
        highlights = []
        for item in doc.get('inner_hits', {}).values():
            for hit in item['hits']['hits']:
                highlights += hit.get('highlight', {}) \
                              .get('ingredients.ingredient', [])
        for highlight in highlights:
            bs = BeautifulSoup(highlight)
            matches += [em.text.lower() for em in bs.findAll('em')]
        return {'matches': list(set(matches))}

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
    def _generate_include_clause(include):
        highlight = {'type': 'fvh', 'fields': {'ingredients.ingredient': {}}}
        return [{
            'nested': {
                'path': 'ingredients',
                'query': {
                    'constant_score': {
                        'filter': {
                            'match_phrase': {'ingredients.ingredient': inc}
                        }
                    }
                },
                'inner_hits': {'highlight': highlight, 'name': inc},
                'score_mode': 'max'
            }
        } for inc in include]

    @staticmethod
    def _generate_exclude_clause(exclude):
        return [{
            'nested': {
                'path': 'ingredients',
                'query': {'match_phrase': {'ingredients.ingredient': exc}}
            }
        } for exc in exclude]

    def search(self, include, exclude, secondary=False):
        index = self.noun
        if secondary:
            index += '-secondary'

        include = self._generate_include_clause(include)
        exclude = self._generate_exclude_clause(exclude)

        results = self.es.search(
            index=index,
            body={
                'query': {
                    'bool': {
                        'should': include,
                        'must_not': exclude,
                        'filter': [
                            {'range': {'time': {'gte': 5}}},
                            {'wildcard': {'image': '*'}},
                        ],
                        'minimum_should_match': 1 if include else 0
                    }
                }
            }
        )

        return [
            {**self.from_doc(result).to_dict(), **self.matches(result)}
            for result in results['hits']['hits']
        ]
