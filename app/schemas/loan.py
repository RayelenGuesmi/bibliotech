from datetime import datetime
from pydantic import BaseModel, ConfigDict


# Ce que le client envoie pour emprunter : juste qui et quel livre
class LoanCreate(BaseModel):
    user_id: int
    book_id: int


# Ce que l'API renvoie
class LoanRead(BaseModel):
    id: int
    user_id: int
    book_id: int
    loan_date: datetime
    return_date: datetime | None = None
    is_returned: bool

    model_config = ConfigDict(from_attributes=True)