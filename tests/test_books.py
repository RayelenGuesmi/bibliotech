def test_create_book(client, test_book):
    # Assert : le livre créé a bien un id et les bons champs
    assert test_book["id"] is not None
    assert test_book["title"] == "PYTEST Livre"
    assert test_book["available"] is True


def test_list_books_contains_created_book(client, test_book):
    # Act
    response = client.get("/books/")
    # Assert
    assert response.status_code == 200
    ids = [b["id"] for b in response.json()]
    assert test_book["id"] in ids


def test_search_books_by_genre(client, test_book):
    # Act : recherche par le genre du livre de test
    response = client.get("/books/", params={"genre": "Test"})
    # Assert
    assert response.status_code == 200
    titles = [b["title"] for b in response.json()]
    assert "PYTEST Livre" in titles


def test_search_books_no_match(client, test_book):
    # Act : recherche sur un genre qui ne correspond à rien
    response = client.get("/books/", params={"genre": "Inexistant"})
    # Assert
    assert response.status_code == 200
    assert response.json() == [] or all(
        b["title"] != "PYTEST Livre" for b in response.json()
    )