import pytest

from datetime import datetime, timedelta

from reciperadar.recipe import Recipe
from reciperadar.reminders import MealReminder


@pytest.fixture
def future_meal_args(raw_recipe_hit):
    recipe = Recipe.from_doc(raw_recipe_hit)
    today_dt = datetime.combine(datetime.today(), datetime.min.time())
    future_meal_dt = today_dt + timedelta(weeks=1, hours=18)

    return {
        'recipe': recipe,
        'recipients': ['test@example.com'],
        'start_time': future_meal_dt,
        'timezone': 'Europe/London',
    }


def test_construct_mealreminder(future_meal_args):
    MealReminder(**future_meal_args)
