from reciperadar.models.recipes import Recipe


def test_recipe_from_doc(raw_recipe_hit):
    Recipe().from_doc(raw_recipe_hit['_source'])


def test_image_ext(raw_recipe_hit):
    r = Recipe().from_doc(raw_recipe_hit['_source'])
    assert r.image_ext == 'png'
