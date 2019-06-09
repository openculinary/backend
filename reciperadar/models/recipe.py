from base58 import b58encode
from bs4 import BeautifulSoup
import mmh3
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
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

    def from_ingredient(ingredient):
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
    def from_json(data):
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
            ],
            time=data['time'],
        )

    @staticmethod
    def from_doc(doc):
        matches = []
        highlights = []
        if 'inner_hits' in doc:
            for inner_hit in doc['inner_hits']['ingredients']['hits']['hits']:
                highlights += inner_hit.get('highlight', {}) \
                              .get('ingredients.ingredient', [])
        for highlight in highlights:
            bs = BeautifulSoup(highlight)
            matches += [em.text.lower() for em in bs.findAll('em')]
        matches = list(set(matches))

        source = doc.pop('_source')
        return {
            'id': doc['_id'],
            'image': source['image'],
            'ingredients': source['ingredients'],
            'matches': matches,
            'title': source['title'],
            'time': source['time'],
            'url': source['url'],
        }

    def to_json(self):
        data = super().to_json()
        data['ingredients'] = [
            ingredient.to_json()
            for ingredient in self.ingredients
        ]
        return data

    def search(self, include, exclude, secondary=False):
        index = self.noun
        if secondary:
            index += '-secondary'

        match_field = 'ingredients.ingredient'
        include = [{'match_phrase': {match_field: inc}} for inc in include]
        exclude = [{'match_phrase': {match_field: exc}} for exc in exclude]
        highlight = {'type': 'fvh', 'fields': {match_field: {}}}

        results = self.es.search(
            index=index,
            body={
                'query': {'bool': {'must': [{
                    'nested': {
                        'path': 'ingredients',
                        'query': {
                            'bool': {
                                'should': include,
                                'must_not': exclude,
                            }
                        },
                        'inner_hits': {'highlight': highlight}
                    }
                }, {
                    'bool': {
                        'filter': [
                            {'range': {'time': {'gte': 5}}},
                            {'wildcard': {'image': '*'}},
                        ]
                    }
                }]}}
            }
        )

        return [
            self.from_doc(result)
            for result in results['hits']['hits']
        ]
