from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.loan import LoanCreate, LoanRead
from app.crud import loan as loan_crud
from app.crud.loan import LoanError

router = APIRouter(prefix="/loans", tags=["Emprunts"])


@router.post("/", response_model=LoanRead, status_code=status.HTTP_201_CREATED)
def borrow_book(loan: LoanCreate, db: Session = Depends(get_db)):
    try:
        return loan_crud.create_loan(db, loan)
    except LoanError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{loan_id}/return", response_model=LoanRead)
def return_book(loan_id: int, db: Session = Depends(get_db)):
    try:
        return loan_crud.return_loan(db, loan_id)
    except LoanError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=list[LoanRead])
def user_history(user_id: int, db: Session = Depends(get_db)):
    return loan_crud.get_user_loans(db, user_id)


@router.get("/{loan_id}", response_model=LoanRead)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    db_loan = loan_crud.get_loan(db, loan_id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Emprunt introuvable")
    return db_loan