def test_retrieve_product_hierarchy(client):
    response = client.get(path="/products/hierarchy")

    assert response.status_code == 200
