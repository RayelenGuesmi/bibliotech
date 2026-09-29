import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.models.book import Book
from app.models.loan import Loan


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture
def test_book(client):
    # Arrange : crée un livre de test via l'API
    response = client.post(
        "/books/",
        json={"title": "PYTEST Livre", "author": "PYTEST Auteur", "genre": "Test"},
    )
    book = response.json()
    yield book
    # Teardown : supprime le livre créé pour ne pas polluer la base
    db = SessionLocal()
    db.query(Book).filter(Book.id == book["id"]).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_user(client):
    # Email unique à chaque run pour éviter les collisions si un test précédent
    # a planté avant son nettoyage
    email = f"pytest_{uuid.uuid4().hex[:8]}@example.com"
    response = client.post(
        "/users/",
        json={"name": "PYTEST User", "email": email, "password": "testpass123"},
    )
    user = response.json()
    yield user
    db = SessionLocal()
    db.query(User).filter(User.id == user["id"]).delete()
    db.commit()
    db.close()


@pytest.fixture
def test_loan(client, test_user, test_book):
    # Dépend de test_user et test_book : pytest nettoiera dans l'ordre inverse
    # (emprunt supprimé avant le livre/user, respect des clés étrangères)
    response = client.post(
        "/loans/", json={"user_id": test_user["id"], "book_id": test_book["id"]}
    )
    loan = response.json()
    yield loan
    db = SessionLocal()
    db.query(Loan).filter(Loan.id == loan["id"]).delete()
    db.commit()
    db.close()