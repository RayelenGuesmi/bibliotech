from datetime import datetime
from sqlalchemy.orm import Session

from app.models.loan import Loan
from app.models.book import Book
from app.models.user import User
from app.schemas.loan import LoanCreate


class LoanError(Exception):
    """Erreur métier liée aux emprunts."""
    pass


def create_loan(db: Session, loan: LoanCreate) -> Loan:
    # 1. L'utilisateur existe-t-il ?
    user = db.query(User).filter(User.id == loan.user_id).first()
    if user is None:
        raise LoanError("Utilisateur introuvable")

    # 2. Le livre existe-t-il ?
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    if book is None:
        raise LoanError("Livre introuvable")

    # 3. Le livre est-il disponible ? (règle métier centrale)
    if not book.available:
        raise LoanError("Ce livre n'est pas disponible")

    # 4. Créer l'emprunt et marquer le livre indisponible
    db_loan = Loan(user_id=loan.user_id, book_id=loan.book_id)
    book.available = False
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan


def return_loan(db: Session, loan_id: int) -> Loan:
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if loan is None:
        raise LoanError("Emprunt introuvable")
    if loan.is_returned:
        raise LoanError("Cet emprunt a déjà été rendu")

    # Marquer rendu + rendre le livre à nouveau disponible
    loan.is_returned = True
    loan.return_date = datetime.utcnow()
    book = db.query(Book).filter(Book.id == loan.book_id).first()
    if book:
        book.available = True
    db.commit()
    db.refresh(loan)
    return loan


def get_user_loans(db: Session, user_id: int) -> list[Loan]:
    """Historique complet des emprunts d'un utilisateur."""
    return db.query(Loan).filter(Loan.user_id == user_id).all()


def get_loan(db: Session, loan_id: int) -> Loan | None:
    return db.query(Loan).filter(Loan.id == loan_id).first()