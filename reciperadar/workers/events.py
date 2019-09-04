from reciperadar.services.database import Database
from reciperadar.workers.broker import celery


@celery.task
def store_event(event):
    session = Database().get_session()
    session.add(event)
    session.commit()
    session.close()
