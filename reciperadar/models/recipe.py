from base58 import b58encode
import inflect
import mmh3
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
    ingredient_id = Column(String, fk, index=True)

    id = Column(String, primary_key=True)
    parser = Column(String)
    raw = Column(String)
    is_plural = Column(Boolean)
    singular = Column(String)
    plural = Column(String)

    STATE_AVAILABLE = 'available'
    STATE_REQUIRED = 'required'

    state = None

    inflector = inflect.engine()

    @staticmethod
    def from_doc(doc, matches=None):
        parser = doc.get('parser')
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
            True: IngredientProduct.STATE_AVAILABLE,
            False: IngredientProduct.STATE_REQUIRED,
        }
        state = states[singular in matches or plural in matches]

        product_id = b58encode(uuid4().bytes).decode('utf-8')
        return IngredientProduct(
            id=product_id,
            parser=parser,
            raw=raw,
            is_plural=is_plural,
            singular=singular,
            plural=plural,
            state=state
        )


class RecipeIngredient(Storable):
    __tablename__ = 'recipe_ingredients'

    fk = ForeignKey('recipes.id', ondelete='cascade')
    recipe_id = Column(String, fk, index=True)

    id = Column(String, primary_key=True)
    description = Column(String)
    product = relationship(
        'IngredientProduct',
        backref='recipe_ingredient',
        uselist=False,
        passive_deletes='all'
    )

    quantity = Column(Float)
    quantity_parser = Column(String)
    units = Column(String)
    units_parser = Column(String)
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
        if not self.product:
            return None

        tokens = []
        if self.quantity:
            tokens.append({
                'type': 'quantity',
                'value': self.quantity,
            })
            tokens.append({
                'type': 'text',
                'value': ' ',
            })

        if self.units:
            tokens.append({
                'type': 'units',
                'value': self.units,
            })
            tokens.append({
                'type': 'text',
                'value': ' ',
            })

        tokens.append({
            'type': 'product',
            'value': self.product.raw,
            'state': self.product.state,
            'singular': self.product.singular,
            'plural': self.product.plural,
        })
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
    domain = Column(String)
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

    @property
    def products(self):
        products = set()
        for ingredient in self.ingredients:
            products.add(ingredient.product.singular)
        return list(products)

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

        src_info = tldextract.extract(data['src'])

        recipe_id = b58encode(mmh3.hash_bytes(data['src'])).decode('utf-8')
        return Recipe(
            id=recipe_id,
            title=data['title'],
            src=data['src'],
            domain=f'{src_info.domain}.{src_info.suffix}',
            image=data.get('image'),
            ingredients=list(ingredients.values()),
            servings=data['servings'],
            time=data['time'],
        )

    @staticmethod
    def matches(doc, includes):
        return [
            content['derived_from']
            for content in doc['_source']['contents']
            if content['product'] in set(includes)
        ]

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
        return {
            'id': self.id,
            'title': self.title,
            'time': self.time,
            'image': f'images/recipes/{self.id[:2]}/{self.id}.webp',
            'ingredients': [
                ingredient.to_dict()
                for ingredient in self.ingredients
            ],
            'servings': self.servings,
            'src': self.src,
            'domain': self.domain,
            'url': self.url,
        }

    @property
    def contents(self):
        expansions = {
            'bacon': 'meat',
            'beef': 'meat',
            'chicken': 'meat',
            'pork': 'meat',
        }

        results = {}
        for product in self.products:
            results[product] = product
            for key in expansions:
                if key in product:
                    results[key] = product
                    results[expansions[key]] = product
                    break

        return [{
            'product': expansion,
            'derived_from': product
        } for expansion, product in results.items()]

    def _ingredients_to_doc(self):
        return [
            ingredient.to_doc()
            for ingredient in self.ingredients
        ]

    def to_doc(self):
        data = super().to_doc()
        data['ingredients'] = self._ingredients_to_doc()
        data['contents'] = self.contents
        data['products'] = self.products
        data['product_count'] = len(self.products)
        return data

    @staticmethod
    def _generate_should_clause(include):
        if not include:
            return {'match_all': {}}

        # sum the score of query ingredients found in the recipe
        return [{
            'constant_score': {
                'boost': 1,
                'filter': {'match': {'contents.product': inc}}
            }
        } for inc in include]

    @staticmethod
    def _generate_should_not_clause(include, exclude):
        # match any ingredients in the exclude list
        return [{'match': {'contents.product': exc}} for exc in exclude]

    @staticmethod
    def _generate_sort_params(include, sort):
        # don't score relevance searches if no query ingredients are provided
        if sort == 'relevance' and not include:
            return {'script': '0', 'order': 'desc'}

        preamble = '''
            def inv_score = 1 / (_score + 1);
            def product_count = doc.product_count.value;
            def missing_count = product_count - _score;

            def missing_ratio = missing_count / product_count;
            def present_ratio = _score / product_count;
        '''
        sort_configs = {
            # rank: number of ingredient matches
            # tiebreak: percentage of recipe matched
            'relevance': {
                'script': f'{preamble} _score + present_ratio',
                'order': 'desc'
            },

            # rank: number of missing ingredients
            # tiebreak: percentage of recipe matched
            'ingredients': {
                'script': f'{preamble} missing_count + present_ratio',
                'order': 'asc'
            },

            # rank: preparation time
            # tiebreak: percentage of missing ingredients
            'duration': {
                'script': f'{preamble} doc.time.value + missing_ratio',
                'order': 'asc'
            },
        }
        return sort_configs[sort]

    def search(self, include, exclude, offset, limit, sort):
        offset = max(0, offset)
        limit = max(1, limit)
        limit = min(25, limit)
        sort = sort or 'relevance'

        should_clause = self._generate_should_clause(include)
        must_not_clause = self._generate_should_not_clause(include, exclude)
        sort_params = self._generate_sort_params(include, sort)

        query = {
            'function_score': {
                'boost_mode': 'replace',
                'query': {
                    'bool': {
                        'should': should_clause,
                        'must_not': must_not_clause,
                        'filter': [{'range': {'time': {'gte': 5}}}],
                        'minimum_should_match': '1<75%'
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
