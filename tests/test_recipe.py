from reciperadar.models.recipe import Recipe


def test_recipe_from_doc(raw_recipe_hit):
    Recipe().from_doc(raw_recipe_hit)
