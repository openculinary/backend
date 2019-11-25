import pytest
import responses

from reciperadar.workers.queries import recrawl_query

SERVICE_URL = 'http://recrawler-service'


@pytest.fixture
def error_response():
    responses.add(responses.POST, SERVICE_URL, status=400)


@pytest.fixture
def valid_response():
    responses.add(responses.POST, SERVICE_URL, json=['http://www.example.com'])


@responses.activate
def test_recrawler_error_handled(error_response):
    result = recrawl_query(include=['tofu'])

    assert result == []


@responses.activate
def test_recrawler_success(valid_response):
    result = recrawl_query(include=['tofu'])

    assert result == ['http://www.example.com']
