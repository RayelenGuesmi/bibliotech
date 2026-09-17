from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, Identity
from sqlalchemy.orm import relationship

from app.database import Base


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, Identity(), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    loan_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    return_date = Column(DateTime, nullable=True)
    is_returned = Column(Boolean, default=False, nullable=False)

    # Liens inverses vers l'utilisateur et le livre concernés
    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")