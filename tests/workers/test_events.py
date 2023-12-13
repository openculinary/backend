from reciperadar.models.events.search import SearchEvent
from reciperadar.workers.events import store_event


def test_duplicate_event_task(db_session):
    event_table = "searches"
    event_data = {"event_id": "123"}
    assert len(SearchEvent.query.all()) == 0

    store_event(event_table, event_data)
    assert len(SearchEvent.query.all()) == 1

    store_event(event_table, event_data)
    assert len(SearchEvent.query.all()) == 1
