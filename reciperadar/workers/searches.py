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
    response = requests.post(
        url='http://recrawler-service',
        params=params
    )
    try:
        response.raise_for_status()
    except Exception as e:
        print(f'Recrawling failed due to "{e.__class__.__name__}" exception')
        return []
    return response.json()
