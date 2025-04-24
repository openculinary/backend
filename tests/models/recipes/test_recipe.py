import pytest

from reciperadar.models.recipes import Recipe


def test_recipe_from_doc(db_session, raw_recipe_hit):
    recipe = Recipe().from_doc(raw_recipe_hit["_source"])

    # Commit recipe to the session; performs db object relationship resolution
    db_session.add(recipe)
    db_session.commit()

    assert recipe.author == "example"
    assert not recipe.hidden

    # assert recipe.directions[0].equipment[0].name == "skewer"
    # assert recipe.directions[0].equipment[1].name == "oven"
    # assert recipe.directions[0].markup == (
    #     "<mark class='verb action'>place</mark>"
    #     "<mark class='equipment utensil'>skewer</mark>"
    #     "<mark class='equipment appliance'>oven</mark>"
    # )

    assert recipe.ingredients[0].product_name.singular == "one"
    expected_contents = ["one", "ancestor-of-one"]
    actual_contents = recipe.ingredients[0].product_name.contents

    assert all([content in actual_contents for content in expected_contents])

    # expected_equipment_names = ["oven", "skewer"]
    # actual_equipment_names = recipe.equipment_names

    # assert all(
    #     [
    #         equipment_name in actual_equipment_names
    #         for equipment_name in expected_equipment_names
    #     ]
    # )

    assert recipe.ingredients[0].product.is_vegan
    assert not recipe.ingredients[1].product.is_gluten_free

    assert not recipe.is_gluten_free
    assert not recipe.is_vegan
    assert recipe.is_vegetarian


def test_hidden_recipe(db_session, raw_recipe_hit):
    recipe = Recipe().from_doc(raw_recipe_hit["_source"])

    # Commit recipe to the session; performs db object relationship resolution
    db_session.add(recipe)
    db_session.commit()

    recipe.ingredients[0].product = None

    doc = recipe.to_doc()
    assert doc.get("hidden") is True


@pytest.mark.parametrize(
    ("not_found", "should_write", "value"),
    [
        (True, True, True),
        (False, False, None),
    ],
)
def test_recipe_found_state(db_session, raw_recipe_hit, not_found, should_write, value):
    recipe = Recipe().from_doc(raw_recipe_hit["_source"])

    # Commit recipe to the session; performs db object relationship resolution
    db_session.add(recipe)
    db_session.commit()

    recipe.not_found = not_found

    doc = recipe.to_doc()
    was_written = "not_found" in doc
    actual_value = doc.get("not_found")

    assert was_written == should_write
    assert actual_value == value
