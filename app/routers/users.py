from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserRead
from app.crud import user as user_crud

router = APIRouter(prefix="/users", tags=["Utilisateurs"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Refuse un email déjà utilisé
    if user_crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    return user_crud.create_user(db, user)


@router.get("/", response_model=list[UserRead])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_crud.get_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return db_user