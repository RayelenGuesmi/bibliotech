from datetime import datetime
from pydantic import BaseModel, ConfigDict


class LoanCreate(BaseModel):
    user_id: int
    book_id: int


class LoanRead(BaseModel):
    id: int
    user_id: int
    book_id: int
    loan_date: datetime
    due_date: datetime
    return_date: datetime | None = None
    is_returned: bool

    model_config = ConfigDict(from_attributes=True)