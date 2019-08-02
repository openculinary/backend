from base58 import b58encode
from bs4 import BeautifulSoup
import inflect
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
import tldextract
from uuid import uuid4

from reciperadar.models.base import Searchable, Storable


class IngredientProduct(Storable):
    __tablename__ = 'ingredient_products'

    fk = ForeignKey('recipe_ingredients.id', ondelete='cascade')
    ingredient_id = Column(String, fk)

    id = Column(String, primary_key=True)
    raw = Column(String)
    is_plural = Column(Boolean)
    singular = Column(String)
    plural = Column(String)

    STATE_MATCHED = 'matched'
    STATE_REQUIRED = 'required'

    state = None

    inflector = inflect.engine()

    @staticmethod
    def from_doc(doc, matches=None):
        raw = doc.get('raw')
        is_plural = doc.get('is_plural')
        singular = doc.get('singular')
        plural = doc.get('plural')

        if not singular or not plural:
            singular = IngredientProduct.inflector.singular_noun(raw) or raw
            plural = IngredientProduct.inflector.plural_noun(singular)
            is_plural = raw == plural

        matches = matches or []
        states = {
            True: IngredientProduct.STATE_MATCHED,
            False: IngredientProduct.STATE_REQUIRED,
        }
        state = states[singular in matches or plural in matches]

        product_id = b58encode(uuid4().bytes).decode('utf-8')
        return IngredientProduct(
            id=product_id,
            raw=raw,
            is_plural=is_plural,
            singular=singular,
            plural=plural,
            state=state
        )


class RecipeIngredient(Storable):
    __tablename__ = 'recipe_ingredients'

    fk = ForeignKey('recipes.id', ondelete='cascade')
    recipe_id = Column(String, fk)

    id = Column(String, primary_key=True)
    description = Column(String)
    product = relationship(
        'IngredientProduct',
        backref='recipe_ingredient',
        uselist=False,
        passive_deletes='all'
    )

    quantity = Column(Float)
    units = Column(String)
    verb = Column(String)

    inflector = inflect.engine()

    @staticmethod
    def from_doc(doc, matches=None):
        description = doc['description'].strip()
        product = doc.get('product')
        quantity = doc.get('quantity')
        units = doc.get('units')
        verb = doc.get('verb')

        if product:
            product = IngredientProduct.from_doc(product, matches)

        ingredient_id = b58encode(uuid4().bytes).decode('utf-8')
        return RecipeIngredient(
            id=ingredient_id,
            description=description,
            product=product,
            quantity=quantity,
            units=units,
            verb=verb
        )

    def to_dict(self):
        if self.product and self.product.raw in self.description:
            tokens = self.description.split(self.product.raw, 1)
            tokens = [{
                'type': 'text',
                'value': token,
            } for token in tokens if token]
            tokens.insert(1, {
                'type': 'product',
                'value': self.product.raw,
                'state': self.product.state,
            })
        else:
            tokens = [{
                'type': 'text',
                'value': self.description,
            }]
        return {'tokens': tokens}

    def to_doc(self):
        data = super().to_doc()
        data['product'] = self.product.to_doc()
        return data


class Recipe(Storable, Searchable):
    __tablename__ = 'recipes'

    id = Column(String, primary_key=True)
    title = Column(String)
    src = Column(String)
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

    @property
    def url(self):
        return f'/#action=view&id={self.id}'

    @staticmethod
    def from_dict(data):
        # Parse and de-duplicate ingredients
        ingredients = [
            RecipeIngredient.from_doc(ingredient)
            for ingredient in data['ingredients']
            if ingredient['description'].strip()
        ]
        ingredients = {
            ingredient.id: ingredient
            for ingredient in ingredients
        }

        recipe_id = b58encode(uuid4().bytes).decode('utf-8')
        return Recipe(
            id=recipe_id,
            title=data['title'],
            src=data['src'],
            image=data.get('image'),
            ingredients=list(ingredients.values()),
            servings=data['servings'],
            time=data['time'],
        )

    @staticmethod
    def matches(doc, includes):
        highlights = []
        for item in doc.get('inner_hits', {}).values():
            for hit in item['hits']['hits']:
                highlight = hit.get('highlight', {})
                highlights += highlight.get('ingredients.product.singular', [])
                highlights += highlight.get('ingredients.product.plural', [])
        matches = []
        for highlight in highlights:
            bs = BeautifulSoup(highlight, features='html.parser')
            matches += [em.text.lower() for em in bs.findAll('em')]
        return matches

    @staticmethod
    def from_doc(doc, matches=None):
        source = doc.pop('_source')
        return Recipe(
            id=doc['_id'],
            title=source['title'],
            src=source['src'],
            image=source['image'],
            ingredients=[
                RecipeIngredient.from_doc(ingredient, matches)
                for ingredient in source['ingredients']
                if ingredient['description'].strip()
            ],
            servings=source.get('servings'),
            time=source['time']
        )

    def to_dict(self):
        src_info = tldextract.extract(self.src)
        return {
            'id': self.id,
            'title': self.title,
            'time': self.time,
            'image': self.image,
            'ingredients': [
                ingredient.to_dict()
                for ingredient in self.ingredients
            ],
            'src': self.src,
            'domain': '{}.{}'.format(src_info.domain, src_info.suffix),
            'url': self.url,
        }

    def to_doc(self):
        data = super().to_doc()
        data['ingredients'] = [
            ingredient.to_doc()
            for ingredient in self.ingredients
        ]
        data['ingredient_count'] = len(self.ingredients)
        return data

    @staticmethod
    def _generate_must_clause(include):
        if not include:
            return {'match_all': {}}

        highlight = {
            'fields': {
                'ingredients.product.singular': {},
                'ingredients.product.plural': {},
            }
        }
        return {
            # sum the cumulative score of all ingredients which match the query
            'nested': {
                'path': 'ingredients',
                'score_mode': 'sum',
                'query': {
                    # return a constant score for each ingredient which matches
                    'constant_score': {
                        'boost': 1,
                        'filter': {
                            'bool': {
                                'should': [{
                                    # match on singular or plural product names
                                    'multi_match': {
                                        'query': inc,
                                        'fields': [
                                            'ingredients.product.singular',
                                            'ingredients.product.plural',
                                        ]
                                    }
                                } for inc in include]
                            }
                        }
                    }
                },
                # apply highlighting to matched product names
                'inner_hits': {'highlight': highlight, 'size': 25}
            }
        }

    @staticmethod
    def _generate_must_not_clause(include, exclude):
        # match any ingredients in the exclude list
        return [{
            'nested': {
                'path': 'ingredients',
                'query': {
                    # match on singular or plural product names
                    'multi_match': {
                        'query': exc,
                        'fields': [
                            'ingredients.product.singular',
                            'ingredients.product.plural',
                        ]
                    }
                }
            }
        } for exc in exclude]

    @staticmethod
    def _generate_sort_params(include, sort):
        # don't score relevance searches if no query ingredients are provided
        if sort == 'relevance' and not include:
            return {'script': '0', 'order': 'desc'}

        preamble = '''
            def inv_score = 1 / (_score + 1);
            def ingredient_count = doc.ingredient_count.value;
        '''
        sort_configs = {
            # rank: number of ingredient matches
            # tiebreak: percentage of recipe matched
            'relevance': {
                'script': f'{preamble} _score + (_score / ingredient_count)',
                'order': 'desc'
            },

            # rank: number of missing ingredients
            # tiebreak: number of ingredient matches
            'ingredients': {
                'script': f'{preamble} ingredient_count - _score + inv_score',
                'order': 'asc'
            },

            # rank: preparation time
            # tiebreak: number of ingredient matches
            'duration': {
                'script': f'{preamble} doc.time.value + inv_score',
                'order': 'asc'
            },
        }
        return sort_configs[sort]

    def search(self, include, exclude, offset, limit, sort):
        offset = max(0, offset)
        limit = max(1, limit)
        limit = min(25, limit)
        sort = sort or 'relevance'

        must_clause = self._generate_must_clause(include)
        must_not_clause = self._generate_must_not_clause(include, exclude)
        sort_params = self._generate_sort_params(include, sort)

        query = {
            'function_score': {
                'boost_mode': 'replace',
                'query': {
                    'bool': {
                        'must': must_clause,
                        'must_not': must_not_clause,
                        'filter': [{'range': {'time': {'gte': 5}}}]
                    }
                },
                'script_score': {'script': {'source': sort_params['script']}}
            }
        }
        sort = [{'_score': sort_params['order']}]

        results = self.es.search(
            index=self.noun,
            body={
                'from': offset,
                'size': limit,
                'query': query,
                'sort': sort,
            }
        )

        recipes = []
        for result in results['hits']['hits']:
            matches = self.matches(result, include)
            recipe = Recipe.from_doc(result, matches)
            recipes.append(recipe.to_dict())

        return {
            'total': min(results['hits']['total']['value'], 50 * limit),
            'results': recipes
        }
