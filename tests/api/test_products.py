def test_retrieve_empty_product_hierarchy(client):
    response = client.get(path="/products/hierarchy")
    products = response.data.decode("utf-8").splitlines()

    assert response.status_code == 200
    assert len(products) == 0
