from reciperadar import db
from reciperadar.models.events.redirect import RedirectEvent
from reciperadar.models.events.search import SearchEvent
from reciperadar.workers.broker import celery


event_table_classes = {
    "redirects": RedirectEvent,
    "searches": SearchEvent,
}


@celery.task
def store_event(event_table, event_data):
    if event_table not in event_table_classes:
        return
    event = event_table_classes[event_table](**event_data)

    db.session.add(event)
    db.session.commit()
    db.session.close()
