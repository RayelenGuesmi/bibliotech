from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# Le "moteur" = la connexion à Oracle
engine = create_engine(settings.database_url, echo=True)

# Une "session" = une conversation avec la BDD (une par requête HTTP)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# La classe de base dont hériteront tous nos modèles (tables)
Base = declarative_base()


# Dépendance FastAPI : ouvre une session, la donne à la route, la ferme après
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()