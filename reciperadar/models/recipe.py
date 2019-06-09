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
    def matches(doc):
        matches = []
        highlights = []
        if 'inner_hits' in doc:
            for inner_hit in doc['inner_hits']['ingredients']['hits']['hits']:
                highlights += inner_hit.get('highlight', {}) \
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
            {**self.from_doc(result).to_dict(), **self.matches(result)}
            for result in results['hits']['hits']
        ]
