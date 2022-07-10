from celery import Celery

celery = Celery("reciperadar", broker="pyamqp://guest@rabbitmq")
