from reciperadar.models.events.redirect import RedirectEvent
from reciperadar.models.events.search import SearchEvent
from reciperadar.services.database import Database
from reciperadar.workers.broker import celery


event_table_classes = {
    'redirects': RedirectEvent,
    'searches': SearchEvent,
}


@celery.task
def store_event(event_table, event_data):
    if event_table not in event_table_classes:
        return
    event = event_table_classes[event_table](**event_data)

    session = Database().get_session()
    session.add(event)
    session.commit()
    session.close()
