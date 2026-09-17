from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None


# Ce que le client envoie pour s'inscrire (avec mot de passe en clair)
class UserCreate(UserBase):
    password: str


# Ce que l'API renvoie : PAS de mot de passe
class UserRead(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)