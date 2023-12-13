from sqlalchemy.exc import IntegrityError

from reciperadar import db
from reciperadar.models.events.redirect import RedirectEvent
from reciperadar.models.events.search import SearchEvent
from reciperadar.workers.broker import celery


event_table_classes = {
    "redirects": RedirectEvent,
    "searches": SearchEvent,
}


@celery.task(
    autoretry_for=(Exception,),  # retry all exceptions
    max_retries=None,  # retry forever
    retry_backoff=True,  # enable exponential retry backoff
    retry_backoff_max=600,  # maximum retry delay (upper-limit on exponential backoff)
    retry_jitter=True,  # ensure that backlogged events are not retried simultaneously
)
def store_event(event_table, event_data):
    if event_table not in event_table_classes:
        return
    event = event_table_classes[event_table](**event_data)

    try:
        db.session.add(event)
        db.session.commit()
    except IntegrityError as e:
        if "already exists" not in str(e):
            raise
    except Exception as e:
        print(f"Failed to write {event.__class__.__name__}: {str(e)}")
        raise
    finally:
        db.session.close()
