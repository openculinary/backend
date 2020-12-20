import requests

from reciperadar.workers.broker import celery


@celery.task(queue='recrawl_search')
def recrawl_search(include, exclude, equipment, offset):
    params = {
        'include[]': include,
        'exclude[]': exclude,
        'equipment[]': equipment,
        'offset': offset
    }
    try:
        response = requests.post(
            url='http://recrawler-service',
            params=params
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f'Recrawling failed due to "{e.__class__.__name__}" exception')
        return []
