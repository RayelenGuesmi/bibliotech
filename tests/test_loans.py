def test_borrow_book_makes_it_unavailable(client, test_loan, test_book):
    # Arrange/Act : test_loan a déjà emprunté test_book (via la fixture)
    response = client.get(f"/books/{test_book['id']}")
    # Assert
    assert response.status_code == 200
    assert response.json()["available"] is False


def test_double_borrow_fails(client, test_loan, test_user, test_book):
    # Arrange : test_book est déjà emprunté par test_loan
    # Act : on tente un second emprunt du même livre (par un autre user, peu importe)
    response = client.post(
        "/loans/", json={"user_id": test_user["id"], "book_id": test_book["id"]}
    )
    # Assert
    assert response.status_code == 400


def test_return_book(client, test_loan, test_book):
    # Act
    response = client.post(f"/loans/{test_loan['id']}/return")
    # Assert
    assert response.status_code == 200
    assert response.json()["is_returned"] is True

    # Le livre redevient disponible après le retour
    book_response = client.get(f"/books/{test_book['id']}")
    assert book_response.json()["available"] is True