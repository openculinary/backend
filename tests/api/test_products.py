import json


def test_retrieve_product_hierarchy(client, products):
    expected_product_ids = {"one", "two", "ancestor_of_one"}

    response = client.get(path="/products/hierarchy")
    products = response.data.decode("utf-8").splitlines()
    product_ids = {json.loads(product)["id"] for product in products}

    assert response.status_code == 200
    assert len(products) == 3
    assert product_ids == expected_product_ids
