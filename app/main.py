from fastapi import FastAPI

from app.routers import books

app = FastAPI(
    title="Bibliotech API",
    description="API de gestion de bibliothèque en ligne — Projet 5BDDD",
    version="1.0.0",
)

app.include_router(books.router)


@app.get("/")
def root():
    return {"message": "Bibliotech API — voir /docs pour la documentation"}