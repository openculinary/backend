from flask import current_app
import json
from unittest.mock import patch

from reciperadar.models.recipes.product import ProductName


def mock_query():
    """
    Generator method that lazily performs a flask application context lookup, to
    replicate bug https://github.com/openculinary/backend/issues/65 and then yields
    mock data.
    """
    current_app._get_current_object()
    yield from [
        # name, nutrition, count, plural_count
        (ProductName(id="butter"), None, 1, 1),
        (ProductName(id="orange"), None, 5, 2),
        (ProductName(id="apple"), None, 5, 3),
    ]


@patch("reciperadar.api.products.db.session.query")
def test_retrieve_product_hierarchy(query, client):
    (
        query.return_value.join.return_value.join.return_value.group_by.return_value
    ).all.return_value = mock_query()
    expected_product_ids = {"apple", "butter", "orange"}

    response = client.get(path="/products/hierarchy")
    products = response.data.decode("utf-8").splitlines()
    product_ids = {json.loads(product)["id"] for product in products}

    assert response.status_code == 200
    assert len(products) == 3
    assert product_ids == expected_product_ids
