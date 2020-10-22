from celery import Celery
from celery.signals import task_postrun

celery = Celery('reciperadar', broker='pyamqp://guest@rabbitmq')
postrun = task_postrun
