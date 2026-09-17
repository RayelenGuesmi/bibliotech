from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    result = conn.execute(text("SELECT 'Connexion OK depuis Python' FROM dual"))
    print(result.scalar())