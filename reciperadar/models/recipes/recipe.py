from io import BytesIO
from mmh3 import hash_bytes
import os
from PIL import Image
import requests
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from reciperadar.models.base import Searchable, Storable
from reciperadar.models.recipes.direction import RecipeDirection
from reciperadar.models.recipes.ingredient import RecipeIngredient
from reciperadar.models.recipes.product import IngredientProduct


class Recipe(Storable, Searchable):
    __tablename__ = 'recipes'

    STATIC_DIR = 'reciperadar/static'
    IMAGE_DIR = 'images/recipes'

    id = Column(String, primary_key=True)
    title = Column(String)
    src = Column(String)
    domain = Column(String)
    image_src = Column(String)
    time = Column(Integer)
    servings = Column(Integer)
    ingredients = relationship(
        'RecipeIngredient',
        backref='recipe',
        passive_deletes='all'
    )
    directions = relationship(
        'RecipeDirection',
        backref='recipe',
        passive_deletes='all'
    )

    indexed_at = Column(DateTime)

    @property
    def noun(self):
        return 'recipes'

    @property
    def url(self):
        return f'/#action=view&id={self.id}'

    @property
    def products(self):
        products_by_id = {
            ingredient.product.singular: IngredientProduct(
                product=ingredient.product.product,
                singular=ingredient.product.singular,
            )
            for ingredient in self.ingredients
        }
        return list(products_by_id.values())

    @staticmethod
    def from_doc(doc):
        recipe_id = doc.get('id') or Recipe.generate_id(hash_bytes(doc['src']))
        return Recipe(
            id=recipe_id,
            title=doc['title'],
            src=doc['src'],
            domain=doc['domain'],
            # TODO: Remove fallback 'image' field
            image_src=doc.get('image_src') or doc.get('image'),
            ingredients=[
                RecipeIngredient.from_doc(ingredient)
                for ingredient in doc['ingredients']
                if ingredient['description'].strip()
            ],
            directions=[
                RecipeDirection.from_doc(direction)
                for direction in doc.get('directions') or []
                if direction['description'].strip()
            ],
            servings=doc['servings'],
            time=doc['time']
        )

    def to_dict(self, include=None):
        return {
            'id': self.id,
            'title': self.title,
            'time': self.time,
            'ingredients': [
                ingredient.to_dict(include)
                for ingredient in self.ingredients
            ],
            'directions': [
                direction.to_dict()
                for direction in self.directions
            ],
            'servings': self.servings,
            'src': self.src,
            'domain': self.domain,
            'url': self.url,
            'image_url': self.image_url,
        }

    @property
    def image_url(self):
        return f'{self.IMAGE_DIR}/{self.id[:2]}/{self.id}.webp'

    @property
    def image_filename(self):
        return f'{self.STATIC_DIR}/{self.image_url}'

    @property
    def image_exists(self):
        return os.path.exists(self.image_filename)

    def _request_image_data(self):
        product = 'Mozilla/5.0'
        system = 'Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7'
        platform = 'Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': f'{product} ({system}) {platform}'}

        image_response = requests.get(
            url=self.image_src,
            timeout=0.25,
            headers=headers
        )
        image_response.raise_for_status()
        return image_response.content

    def _save_image_data(self, content):
        image = Image.open(BytesIO(content))
        os.makedirs(os.path.dirname(self.image_filename), exist_ok=True)
        image.save(self.image_filename, 'webp')

    def download_image(self):
        if self.image_exists:
            return True
        try:
            image_data = self._request_image_data()
            self._save_image_data(image_data)
        except Exception:
            print(f'Image download failed for url={self.image_src}')
            return False
        return self.image_exists

    @property
    def contents(self):
        contents = set()
        for product in self.products:
            contents |= set(product.contents)
        return list(contents)

    def to_doc(self):
        data = super().to_doc()
        data['directions'] = [
            direction.to_doc()
            for direction in self.directions
        ]
        data['ingredients'] = [
            ingredient.to_doc()
            for ingredient in self.ingredients
        ]
        data['contents'] = self.contents
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
                'filter': {'match': {'contents': inc}}
            }
        } for inc in include]

    @staticmethod
    def _generate_should_not_clause(include, exclude):
        # match any ingredients in the exclude list
        return [{'match': {'contents': exc}} for exc in exclude]

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
                        'filter': [
                            {'range': {'time': {'gte': 5}}},
                            {'range': {'product_count': {'gt': 0}}},
                        ],
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
            recipe = Recipe.from_doc(result['_source'])
            recipes.append(recipe.to_dict(include))

        return {
            'total': min(results['hits']['total']['value'], 50 * limit),
            'results': recipes
        }
