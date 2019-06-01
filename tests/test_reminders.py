import pytest

from datetime import datetime, timedelta

from reciperadar.reminders import MealReminder


@pytest.fixture
def future_meal_args():
    today_dt = datetime.combine(datetime.today(), datetime.min.time())
    future_meal_dt = today_dt + timedelta(weeks=1, hours=18)
    future_meal_dur = timedelta(hours=1, minutes=30)

    return {
        'title': 'Test Meal',
        'start_time': future_meal_dt,
        'duration': future_meal_dur,
        'recipients': ['test@example.com']
    }


def test_construct_mealreminder(future_meal_args):
    MealReminder(**future_meal_args)
