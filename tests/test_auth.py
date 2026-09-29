def test_login_success(client, test_user):
    # Act
    response = client.post(
        "/auth/login",
        data={"username": test_user["email"], "password": "testpass123"},
    )
    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    # Act
    response = client.post(
        "/auth/login",
        data={"username": test_user["email"], "password": "mauvais_mdp"},
    )
    # Assert
    assert response.status_code == 401