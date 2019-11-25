import requests

from reciperadar.workers.broker import celery


@celery.task(queue='recrawl_search')
def recrawl_search(include):
    params = {'include[]': include}
    response = requests.post('http://recrawler-service', params=params)

    try:
        response.raise_for_status()
    except Exception as e:
        print(f'Exception during recrawler request: {e}')
        return []

    return response.json()
