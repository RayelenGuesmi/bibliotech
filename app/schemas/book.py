from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


# Champs communs partagés
class BookBase(BaseModel):
    title: str
    author: str
    genre: str | None = None
    published_at: date | None = None


# Ce que le client envoie pour créer un livre
class BookCreate(BookBase):
    pass


# Ce que le client envoie pour modifier (tout est optionnel)
class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    published_at: date | None = None
    available: bool | None = None


# Ce que l'API renvoie
class BookRead(BookBase):
    id: int
    available: bool
    created_at: datetime

    # Autorise Pydantic à lire directement un objet SQLAlchemy
    model_config = ConfigDict(from_attributes=True)