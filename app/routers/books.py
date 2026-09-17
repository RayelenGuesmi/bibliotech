from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.crud import book as book_crud

router = APIRouter(prefix="/books", tags=["Livres"])


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return book_crud.create_book(db, book)


@router.get("/", response_model=list[BookRead])
def list_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return book_crud.get_books(db, skip=skip, limit=limit)


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    db_book = book_crud.get_book(db, book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    return db_book


@router.put("/{book_id}", response_model=BookRead)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = book_crud.update_book(db, book_id, book)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    return db_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    if not book_crud.delete_book(db, book_id):
        raise HTTPException(status_code=404, detail="Livre introuvable")