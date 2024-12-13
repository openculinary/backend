import pytest
from reciperadar.workers.searches import recrawl_search


@pytest.fixture
def error_response(respx_mock):
    respx_mock.post("/").respond(status_code=400)


@pytest.fixture
def valid_response(respx_mock):
    respx_mock.post("/").respond(json=["http://www.example.test"])


@pytest.mark.respx(base_url="http://recrawler-service", using="httpx")
def test_recrawler_error_handled(error_response):
    result = recrawl_search(
        include=["tofu"],
        exclude=[],
        equipment=[],
        dietary_properties=[],
        offset=0,
    )

    assert result == []


@pytest.mark.respx(base_url="http://recrawler-service", using="httpx")
def test_recrawler_success(valid_response):
    result = recrawl_search(
        include=["tofu"],
        exclude=[],
        equipment=[],
        dietary_properties=[],
        offset=0,
    )

    assert result == ["http://www.example.test"]
