from datetime import timedelta
from sqlalchemy.orm import Session

from app.models.loan import Loan
from app.models.book import Book
from app.models.user import User
from app.schemas.loan import LoanCreate
from app.database import utcnow


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

    # 4. Créer l'emprunt (échéance à +14 jours) et marquer le livre indisponible
    loan_date = utcnow()
    db_loan = Loan(
        user_id=loan.user_id,
        book_id=loan.book_id,
        loan_date=loan_date,
        due_date=loan_date + timedelta(days=14),
    )
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
    loan.return_date = utcnow()
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


def get_overdue_loans(db: Session) -> list[Loan]:
    """Emprunts non rendus dont la date limite est dépassée."""
    return (
        db.query(Loan)
        .filter(Loan.is_returned == False, Loan.due_date < utcnow())
        .all()
    )