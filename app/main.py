from fastapi import FastAPI

from app.routers import books, users, loans, auth

app = FastAPI(
    title="Bibliotech API",
    description="API de gestion de bibliothèque en ligne — Projet 5BDDD",
    version="1.0.0",
)

app.include_router(books.router)
app.include_router(users.router)
app.include_router(loans.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Bibliotech API — voir /docs pour la documentation"}