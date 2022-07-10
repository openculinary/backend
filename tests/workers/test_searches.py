import pytest
from reciperadar.workers.searches import recrawl_search


@pytest.fixture
@pytest.mark.respx(base_url="http://recrawler-service")
def error_response(respx_mock):
    respx_mock.post("/").respond(status_code=400)


@pytest.fixture
@pytest.mark.respx(base_url="http://recrawler-service")
def valid_response(respx_mock):
    respx_mock.post("/").respond(json=["http://www.example.com"])


def test_recrawler_error_handled(error_response):
    result = recrawl_search(include=["tofu"], exclude=[], equipment=[], offset=0)

    assert result == []


def test_recrawler_success(valid_response):
    result = recrawl_search(include=["tofu"], exclude=[], equipment=[], offset=0)

    assert result == ["http://www.example.com"]
