from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


def create_book(db: Session, book: BookCreate) -> Book:
    db_book = Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_book(db: Session, book_id: int) -> Book | None:
    return db.query(Book).filter(Book.id == book_id).first()


def get_books(db: Session, skip: int = 0, limit: int = 100) -> list[Book]:
    return db.query(Book).offset(skip).limit(limit).all()


def update_book(db: Session, book_id: int, book: BookUpdate) -> Book | None:
    db_book = get_book(db, book_id)
    if db_book is None:
        return None
    # Ne met à jour que les champs fournis
    for field, value in book.model_dump(exclude_unset=True).items():
        setattr(db_book, field, value)
    db.commit()
    db.refresh(db_book)
    return db_book

def search_books(
    db: Session,
    title: str | None = None,
    author: str | None = None,
    genre: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Book]:
    query = db.query(Book)

    # Recherche partielle insensible à la casse sur chaque champ fourni
    if title is not None:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author is not None:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if genre is not None:
        query = query.filter(Book.genre.ilike(f"%{genre}%"))

    return query.offset(skip).limit(limit).all()


def delete_book(db: Session, book_id: int) -> bool:
    db_book = get_book(db, book_id)
    if db_book is None:
        return False
    db.delete(db_book)
    db.commit()
    return True