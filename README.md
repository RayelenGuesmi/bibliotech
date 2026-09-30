#  Bibliotech — Système de gestion de bibliothèque en ligne

API REST de gestion de bibliothèque permettant l'inscription d'utilisateurs, la gestion d'un catalogue de livres, et l'emprunt / retour d'ouvrages avec suivi de disponibilité et historique.

Projet réalisé dans le cadre du module **5BDDD** (SUPINFO MSc — Data Engineering).

---

##  Sommaire

- [Fonctionnalités](#-fonctionnalités)
- [Stack technique](#️-stack-technique)
- [Architecture](#️-architecture)
- [Prérequis](#-prérequis)
- [Installation pas à pas](#-installation-pas-à-pas)
- [Lancer l'application](#-lancer-lapplication)
- [Documentation de l'API](#-documentation-de-lapi)
- [Sécurité](#-sécurité)
- [Ingestion de données par scraping](#-ingestion-de-données-par-scraping)
- [Structure de la base de données](#️-structure-de-la-base-de-données)
- [Persistance des données](#-persistance-des-données)
- [Auteurs](#-auteurs)

---

##  Fonctionnalités

**Gestion des utilisateurs**
- Inscription avec nom, email, téléphone
- Mots de passe hachés (bcrypt), jamais stockés en clair
- Consultation des emprunts et de l'historique par utilisateur

**Gestion des livres**
- Ajout, modification, suppression d'un livre (titre, auteur, genre, date de publication, disponibilité)
- Recherche par titre, auteur ou genre
- Consultation détaillée d'un livre

**Gestion des emprunts**
- Emprunt d'un livre (uniquement s'il est disponible)
- Retour d'un livre (mise à jour automatique de la disponibilité)
- Historique complet des emprunts par utilisateur

**Migrations de base de données**
- Schéma versionné et reproductible via Alembic

---

##  Stack technique

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Base de données | Oracle Database Free 23 (26ai) | Stockage relationnel |
| ORM | SQLAlchemy | Mapping objet-relationnel (Python ↔ Oracle) |
| Migrations | Alembic | Versioning du schéma de la base |
| API | FastAPI | Exposition des routes REST |
| Validation | Pydantic | Validation des données entrantes / sortantes |
| Authentification | bcrypt (+ JWT) | Hachage des mots de passe et sécurité des accès |
| Driver BDD | oracledb | Connexion Python → Oracle |
| Conteneurisation | Docker | Instance Oracle isolée et reproductible |
| Ingestion (bonus) | requests + BeautifulSoup | Scraping de données de livres réelles |

---

##  Architecture

Le projet suit une **architecture en couches**, où chaque module a une responsabilité unique. Une requête traverse ces couches dans l'ordre :

```
Client HTTP → Routers (FastAPI) → Schemas (Pydantic) → CRUD → Models (SQLAlchemy) → Oracle
```

```
mini_projet_librairie/
├── docker-compose.yml       # Définition du conteneur Oracle
├── .env                     # Variables d'environnement (NON versionné)
├── .env.example             # Modèle de configuration (versionné)
├── .gitignore
├── requirements.txt         # Dépendances Python
├── alembic.ini              # Configuration Alembic
├── migrations/              # Migrations de schéma
│   └── versions/
├── scripts/
│   └── scrape_books.py      # Script d'ingestion ETL (bonus)
└── app/
    ├── main.py              # Point d'entrée FastAPI
    ├── config.py            # Lecture de la configuration (.env)
    ├── database.py          # Connexion Oracle + session SQLAlchemy
    ├── models/              # Entités : User, Book, Loan (SQLAlchemy)
    ├── schemas/             # Schémas de validation (Pydantic)
    ├── crud/                # Logique d'accès aux données
    ├── routers/             # Routes de l'API
    └── core/                # Sécurité (hachage, JWT)
```

**Pourquoi cette séparation ?** Chaque couche est indépendante et testable isolément :
- Les **models** décrivent les tables.
- Les **schemas** décrivent le contrat de l'API (ce qui entre / sort), séparé du modèle interne.
- Le **crud** isole toute la logique d'accès à la base ; les routes n'écrivent jamais de requête directement.
- Les **routers** exposent les endpoints HTTP.

---

##  Prérequis

- **Python 3.12+**
- **Docker** et **Docker Compose**
- Environ **3 Go** d'espace disque (image Oracle)

---

##  Installation pas à pas

### 1. Cloner le dépôt

```bash
git clone https://github.com/RayelenGuesmi/bibliotech.git
cd bibliotech
```

### 2. Lancer la base de données Oracle

```bash
docker compose up -d
```

>  **Premier lancement** : Oracle met 2 à 4 minutes à s'initialiser. Suivez la progression avec `docker logs -f library-oracle` et attendez le message `DATABASE IS READY TO USE!`.

### 3. Créer le compte applicatif Oracle

Pour des raisons de sécurité, l'application n'utilise pas le compte administrateur mais un compte dédié avec des droits limités.

```bash
docker exec -it library-oracle sqlplus system/LibraryAdmin2026@//localhost:1521/FREEPDB1
```

Puis, dans l'invite SQL :

```sql
CREATE USER library_app IDENTIFIED BY AppLibrary2026;
GRANT CREATE SESSION TO library_app;
GRANT CREATE TABLE, CREATE SEQUENCE, CREATE VIEW TO library_app;
ALTER USER library_app QUOTA UNLIMITED ON USERS;
EXIT
```

### 4. Créer l'environnement virtuel Python

```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate
```

>  Sur Windows, si l'activation est bloquée : `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

### 5. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 6. Configurer les variables d'environnement

Copiez le modèle et renseignez vos valeurs :

```bash
# Windows
copy .env.example .env
# macOS / Linux
cp .env.example .env
```

Contenu attendu du `.env` :

```
DB_USER=library_app
DB_PASSWORD=AppLibrary2026
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=FREEPDB1
```

### 7. Créer les tables (migrations)

```bash
alembic upgrade head
```

Vérifiez que les tables ont bien été créées :

```bash
docker exec -it library-oracle sqlplus library_app/AppLibrary2026@//localhost:1521/FREEPDB1
```
```sql
SELECT table_name FROM user_tables ORDER BY table_name;
EXIT
```
Vous devez voir : `ALEMBIC_VERSION`, `BOOKS`, `LOANS`, `USERS`.

---

##  Lancer l'application

```bash
uvicorn app.main:app --reload
```

L'API est disponible sur **http://localhost:8000**.

---

##  Documentation de l'API

FastAPI génère automatiquement une documentation interactive **Swagger** :

 **http://localhost:8000/docs**

### Principaux endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/users/` | Inscription d'un utilisateur |
| `GET` | `/users/{id}` | Détail d'un utilisateur |
| `POST` | `/books/` | Ajouter un livre |
| `GET` | `/books/` | Lister les livres |
| `GET` | `/books/{id}` | Détail d'un livre |
| `PUT` | `/books/{id}` | Modifier un livre |
| `DELETE` | `/books/{id}` | Supprimer un livre |
| `POST` | `/loans/` | Emprunter un livre |
| `POST` | `/loans/{id}/return` | Retourner un livre |
| `GET` | `/loans/user/{user_id}` | Historique des emprunts d'un utilisateur |

### Scénario d'utilisation type

1. Créer un utilisateur → `POST /users/`
2. Ajouter (ou scraper) des livres → `POST /books/`
3. Emprunter un livre → `POST /loans/` — le livre passe à *indisponible*
4. Tenter de le réemprunter → refus `400` *« Ce livre n'est pas disponible »*
5. Le retourner → `POST /loans/{id}/return` — le livre redevient *disponible*
6. Consulter l'historique → `GET /loans/user/{user_id}`

---

##  Sécurité

- **Compte Oracle applicatif dédié** : l'application utilise `library_app` (droits limités au strict nécessaire), jamais le compte administrateur. Application du **principe du moindre privilège**.
- **Secrets externalisés** : identifiants de connexion dans un fichier `.env` non versionné (`.gitignore`).
- **Mots de passe hachés** : hachage **bcrypt** avec sel unique par utilisateur ; les mots de passe ne sont jamais stockés ni renvoyés en clair.
- **Contrat d'API strict** : les schémas Pydantic garantissent que le hash du mot de passe n'est jamais exposé par l'API.

---

##  Ingestion de données par scraping

Un script d'ingestion **ETL** peuple la base avec des données de livres réelles, scrapées depuis [books.toscrape.com](https://books.toscrape.com) :

```bash
# Le serveur API doit être lancé au préalable
python scripts/scrape_books.py
```

Le pipeline suit le pattern **Extract – Transform – Load** :

- **Extract** — téléchargement du HTML des pages du catalogue (`requests`)
- **Transform** — extraction des données avec `BeautifulSoup`, incluant un **scraping en profondeur** : visite de la page de détail de chaque livre pour récupérer son genre réel depuis le fil d'Ariane
- **Load** — insertion dans la base via l'API (`POST /books/`)

Le script gère l'encodage UTF-8 et applique une pause entre les requêtes pour respecter le serveur source.

---

##  Structure de la base de données

Trois entités reliées entre elles :

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│    USERS     │         │    LOANS     │         │    BOOKS     │
├──────────────┤         ├──────────────┤         ├──────────────┤
│ id (PK)      │────┐    │ id (PK)      │    ┌────│ id (PK)      │
│ name         │    └───<│ user_id (FK) │    │    │ title        │
│ email (uniq) │         │ book_id (FK) │>───┘    │ author       │
│ phone        │         │ loan_date    │         │ genre        │
│ password_hash│         │ return_date  │         │ published_at │
│ created_at   │         │ is_returned  │         │ available    │
└──────────────┘         └──────────────┘         │ created_at   │
                                                  └──────────────┘
```

La table **LOANS** est une table d'association : elle relie un utilisateur et un livre, et porte les informations de l'emprunt (dates, statut de retour). C'est le cœur de la logique métier.

> ℹ Les clés primaires utilisent des colonnes `IDENTITY` (auto-incrément Oracle), déclarées explicitement dans les modèles SQLAlchemy — une spécificité du dialecte Oracle.

---

##  Persistance des données

Les données sont stockées **de manière permanente** grâce à un **volume Docker** (`oracle-data`) monté sur le répertoire de données d'Oracle :

```yaml
volumes:
  - oracle-data:/opt/oracle/oradata
```

| Action | Données conservées ? |
|--------|:--:|
| Arrêt du serveur uvicorn |  |
| `docker compose stop` / `start` |  |
| `docker compose down` / `up` |  |
| Redémarrage de la machine |  |
| `docker compose down -v` |  (le `-v` détruit le volume) |

Le conteneur est jetable, mais les données lui survivent tant que le volume n'est pas explicitement supprimé.

---

##  Auteurs

Projet réalisé en binôme dans le cadre du MSc Data Engineering (SUPINFO).

- **Rayelen Guesmi**
- **Tharshan Sivapalan**

---

