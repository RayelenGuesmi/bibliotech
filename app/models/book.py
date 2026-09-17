from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, Identity
from sqlalchemy.orm import relationship

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, Identity(), primary_key=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    genre = Column(String(100), nullable=True, index=True)
    published_at = Column(Date, nullable=True)
    available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Un livre est concerné par une liste d'emprunts
    loans = relationship("Loan", back_populates="book")