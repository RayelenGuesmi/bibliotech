#  Library API — Système de gestion de bibliothèque en ligne

API REST de gestion de bibliothèque permettant l'inscription d'utilisateurs,
la gestion d'un catalogue de livres, et l'emprunt/retour d'ouvrages avec suivi
de disponibilité et historique.

Projet réalisé dans le cadre du module **5BDDD** (SUPINFO MSc — Data Engineering).

##  Stack technique

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Base de données | Oracle Database Free 23 | Stockage relationnel |
| ORM | SQLAlchemy | Mapping objet-relationnel |
| Migrations | Alembic | Versioning du schéma |
| API | FastAPI | Exposition des routes REST |
| Validation | Pydantic | Validation des données entrantes/sortantes |
| Authentification | JWT (python-jose) + bcrypt | Sécurité des accès |
| Conteneurisation | Docker | Instance Oracle isolée |

##  Architecture

​```
app/
├── config.py        # Configuration (variables d'environnement)
├── database.py      # Connexion Oracle + session SQLAlchemy
├── models/          # Entités (User, Book, Loan)
├── schemas/         # Schémas de validation Pydantic
├── crud/            # Logique d'accès aux données
├── routers/         # Routes de l'API
└── core/            # Sécurité (hashage, JWT)
​```

Architecture en couches : chaque module a une responsabilité unique
(séparation modèles / validation / logique métier / routes).

## Installation

### Prérequis
- Python 3.12+
- Docker

### Étapes

​```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd mini_projet_librairie

# 2. Lancer la base Oracle
docker compose up -d

# 3. Environnement virtuel
python -m venv venv
.\venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
# Créer un fichier .env (voir .env.example)

# 5. Appliquer les migrations
alembic upgrade head
​```

##  Sécurité

- Compte Oracle applicatif dédié (principe du moindre privilège), distinct de l'admin.
- Secrets gérés via variables d'environnement, jamais committés.
- Mots de passe utilisateurs hachés (bcrypt).
- Authentification par jeton JWT.

##  Documentation API

Une fois l'API lancée, la documentation interactive Swagger est disponible sur
`http://localhost:8000/docs`.

