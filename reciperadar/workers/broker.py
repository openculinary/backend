from celery import Celery, Task

from reciperadar import app


# https://flask.palletsprojects.com/en/2.2.x/patterns/celery/
class FlaskTask(Task):
    def __call__(self, *args: object, **kwargs: object) -> object:
        with app.app_context():
            return self.run(*args, **kwargs)


celery = Celery("reciperadar", broker="pyamqp://guest@rabbitmq", task_cls=FlaskTask)
