#  Bibliotech — Système de gestion de bibliothèque en ligne

![Tests](https://github.com/RayelenGuesmi/bibliotech/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Oracle](https://img.shields.io/badge/Oracle-Database_Free_23-red)

API REST de gestion de bibliothèque permettant l'inscription d'utilisateurs, la gestion d'un catalogue de livres, l'emprunt / retour d'ouvrages avec suivi de disponibilité, historique complet et détection des retards.

Projet réalisé dans le cadre du module **5BDDD** (SUPINFO MSc — Data Engineering).

---

## Sommaire

- [Fonctionnalités](#-fonctionnalités)
- [Stack technique](#️-stack-technique)
- [Architecture](#️-architecture)
- [Structure de la base de données](#️-structure-de-la-base-de-données)
- [Prérequis](#-prérequis)
- [Installation pas à pas](#-installation-pas-à-pas)
- [Lancer l'application](#-lancer-lapplication)
- [Documentation de l'API](#-documentation-de-lapi)
- [Tests automatisés](#-tests-automatisés)
- [Sécurité](#-sécurité)
- [Ingestion de données (bonus ETL)](#-ingestion-de-données-bonus-etl)
- [Persistance des données](#-persistance-des-données)
- [Auteurs](#-auteurs)

---

## Fonctionnalités

### Gestion des utilisateurs
- Inscription avec nom, email, numéro de téléphone
- Mots de passe hachés (bcrypt), jamais stockés en clair
- Authentification via JWT (JSON Web Token)
- Consultation des emprunts et de l'historique par utilisateur

### Gestion des livres
- Ajout, modification, suppression d'un livre (titre, auteur, genre, date de publication, disponibilité)
- Recherche par titre, auteur ou genre — partielle et insensible à la casse
- Pagination (`skip` / `limit`) et tri multi-critères (`sort_by`, `order`)
- Consultation du détail d'un livre

### Gestion des emprunts
- Emprunt d'un livre (uniquement s'il est disponible) avec une échéance automatique à **+14 jours**
- Retour d'un livre avec mise à jour automatique de la disponibilité
- Historique complet des emprunts par utilisateur (route protégée par JWT)
- Détection des **emprunts en retard** (non rendus et dont la `due_date` est dépassée)

### Migrations de base de données
- Schéma versionné et reproductible via Alembic
- Migrations portables Oracle / SQLite (pour la CI)

---

## Stack technique

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Base de données | Oracle Database Free 23 (26ai) | Stockage relationnel |
| ORM | SQLAlchemy | Mapping objet-relationnel (Python ↔ Oracle) |
| Migrations | Alembic | Versioning du schéma de la base |
| API | FastAPI | Exposition des routes REST |
| Validation | Pydantic v2 | Validation des données entrantes / sortantes |
| Authentification | bcrypt + JWT (python-jose) | Hachage des mots de passe et sécurisation des accès |
| Driver BDD | oracledb | Connexion Python → Oracle |
| Conteneurisation | Docker | Instance Oracle isolée et reproductible |
| Tests | pytest + httpx | Tests d'intégration automatisés (9 tests) |
| CI | GitHub Actions | Exécution automatique des tests sur chaque push |
| Ingestion (bonus) | requests + BeautifulSoup | Scraping ETL de données de livres réelles |

---

## Architecture

Le projet suit une **architecture en couches**, où chaque module a une responsabilité unique. Une requête HTTP traverse ces couches dans l'ordre :

```
Client HTTP
    │
    ▼
Routers (FastAPI)     ← Exposition des endpoints HTTP
    │
    ▼
Schemas (Pydantic)    ← Validation & sérialisation des données
    │
    ▼
CRUD                  ← Logique d'accès aux données (aucune requête dans les routes)
    │
    ▼
Models (SQLAlchemy)   ← Définition des entités et relations
    │
    ▼
Oracle Database       ← Stockage persistant
```

```
bibliotech/
├── docker-compose.yml           # Conteneur Oracle + volume persistant
├── .env                         # Variables d'environnement (NON versionné)
├── .env.example                 # Modèle de configuration (versionné)
├── .gitignore
├── requirements.txt             # Dépendances Python
├── alembic.ini                  # Configuration Alembic
├── pytest.ini                   # Configuration pytest (pythonpath)
├── JOURNAL.md                   # Journal de bord du projet (15 phases)
│
├── migrations/                  # Migrations Alembic versionnées
│   └── versions/
│       ├── a9aae99c0094_creation_tables_avec_identity.py
│       └── 1df1bbd58a7f_ajout_due_date_sur_loans.py
│
├── scripts/
│   └── scrape_books.py          # Script ETL de scraping (bonus)
│
├── tests/                       # Suite de tests automatisés
│   ├── conftest.py              # Fixtures avec teardown propre
│   ├── test_auth.py             # Tests d'authentification JWT
│   ├── test_books.py            # Tests gestion des livres
│   └── test_loans.py            # Tests logique d'emprunt
│
├── .github/
│   └── workflows/
│       └── tests.yml            # Pipeline CI GitHub Actions
│
└── app/
    ├── main.py                  # Point d'entrée FastAPI
    ├── config.py                # Lecture de la configuration (.env via Pydantic Settings)
    ├── database.py              # Connexion Oracle + session SQLAlchemy + utcnow()
    ├── models/                  # Entités SQLAlchemy
    │   ├── user.py              # → Table USERS
    │   ├── book.py              # → Table BOOKS
    │   └── loan.py              # → Table LOANS
    ├── schemas/                 # Contrats d'API Pydantic (Create / Read / Update)
    │   ├── user.py
    │   ├── book.py
    │   └── loan.py
    ├── crud/                    # Couche d'accès aux données
    │   ├── user.py
    │   ├── book.py
    │   └── loan.py              # Logique métier des emprunts + LoanError
    ├── routers/                 # Routes FastAPI
    │   ├── auth.py              # POST /auth/login
    │   ├── users.py             # CRUD utilisateurs
    │   ├── books.py             # CRUD livres + recherche + tri
    │   └── loans.py             # Emprunts, retours, historique, retards
    └── core/
        └── security.py          # bcrypt, JWT (create_access_token, get_current_user)
```

> **Pourquoi cette séparation ?** Chaque couche est indépendante et testable isolément. Les **models** décrivent les tables. Les **schemas** décrivent le contrat de l'API, séparé du modèle interne (le hash du mot de passe ne sort jamais). Le **crud** isole toute la logique d'accès aux données : les routes n'écrivent jamais de requête SQL directement. Les **routers** se contentent d'exposer les endpoints HTTP et de convertir les erreurs métier en codes HTTP.

---

## Structure de la base de données

Trois entités reliées entre elles :

```
┌──────────────────┐         ┌────────────────────┐         ┌──────────────────┐
│      USERS       │         │       LOANS         │         │      BOOKS       │
├──────────────────┤         ├────────────────────┤         ├──────────────────┤
│ id (PK, IDENTITY)│────┐    │ id (PK, IDENTITY)  │    ┌────│ id (PK, IDENTITY)│
│ name             │    └───<│ user_id (FK)        │    │    │ title            │
│ email (UNIQUE)   │         │ book_id (FK)        │>───┘    │ author           │
│ phone            │         │ loan_date           │         │ genre            │
│ password_hash    │         │ due_date            │         │ published_at     │
│ created_at       │         │ return_date         │         │ available        │
└──────────────────┘         │ is_returned         │         │ created_at       │
                             └────────────────────┘         └──────────────────┘
```

La table **LOANS** est le cœur du système : elle relie un utilisateur et un livre, et porte toute la logique d'emprunt (dates, statut de retour, détection des retards via `due_date`).

> Les clés primaires utilisent des colonnes **`IDENTITY`** (auto-incrément Oracle), déclarées explicitement dans les modèles SQLAlchemy — une spécificité du dialecte Oracle à ne pas confondre avec `SERIAL` (PostgreSQL) ou `AUTOINCREMENT` (SQLite).

---

## Prérequis

- **Python 3.12+**
- **Docker** et **Docker Compose**
- Environ **3 Go** d'espace disque (image Oracle)

---

## Installation pas à pas

### 1. Cloner le dépôt

```bash
git clone https://github.com/RayelenGuesmi/bibliotech.git
cd bibliotech
```

### 2. Lancer la base de données Oracle

```bash
docker compose up -d
```

> ⏳ **Premier lancement** : Oracle met **2 à 4 minutes** à s'initialiser. Suivez la progression avec :
> ```bash
> docker logs -f library-oracle
> ```
> Attendez le message `DATABASE IS READY TO USE!` avant de passer à la suite.

### 3. Créer le compte applicatif Oracle

Pour des raisons de sécurité, l'application n'utilise **pas** le compte administrateur. On crée un compte dédié `library_app` avec uniquement les droits nécessaires (principe du moindre privilège).

```bash
docker exec -it library-oracle sqlplus system/LibraryAdmin2026@//localhost:1521/FREEPDB1
```

Dans l'invite SQL :

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

>  Sur Windows, si l'activation est bloquée par la politique d'exécution :
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

### 5. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 6. Configurer les variables d'environnement

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Contenu attendu du `.env` :

```env
DB_USER=library_app
DB_PASSWORD=AppLibrary2026
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=FREEPDB1
JWT_SECRET_KEY=changez_cette_valeur_en_production
```

>  Le fichier `.env` est dans `.gitignore` et ne doit **jamais** être commité.

### 7. Appliquer les migrations (création des tables)

```bash
alembic upgrade head
```

**Vérification** que les tables ont bien été créées :

```bash
docker exec -it library-oracle sqlplus library_app/AppLibrary2026@//localhost:1521/FREEPDB1
```
```sql
SELECT table_name FROM user_tables ORDER BY table_name;
EXIT
```

Vous devez voir : `ALEMBIC_VERSION`, `BOOKS`, `LOANS`, `USERS`.

---

## Lancer l'application

```bash
uvicorn app.main:app --reload
```

L'API est disponible sur **http://localhost:8000**.

---

## Documentation de l'API

FastAPI génère automatiquement une **documentation interactive Swagger** :

 **http://localhost:8000/docs**

### Tableau complet des endpoints

| Méthode | Endpoint | Auth | Description |
|---------|----------|:----:|-------------|
| `POST` | `/auth/login` | — | Connexion — renvoie un token JWT |
| `POST` | `/users/` | — | Inscription d'un utilisateur |
| `GET` | `/users/{id}` | — | Détail d'un utilisateur |
| `POST` | `/books/` | — | Ajouter un livre |
| `GET` | `/books/` | — | Lister / rechercher / trier les livres |
| `GET` | `/books/{id}` | — | Détail d'un livre |
| `PUT` | `/books/{id}` | — | Modifier un livre |
| `DELETE` | `/books/{id}` | — | Supprimer un livre |
| `POST` | `/loans/` | — | Emprunter un livre |
| `POST` | `/loans/{id}/return` | — | Retourner un livre |
| `GET` | `/loans/user/{user_id}` |  JWT | Historique des emprunts d'un utilisateur |
| `GET` | `/loans/overdue` | — | Liste des emprunts en retard |
| `GET` | `/loans/{id}` | — | Détail d'un emprunt |

### Paramètres de recherche et tri sur `GET /books/`

| Paramètre | Type | Description |
|-----------|------|-------------|
| `title` | `string` | Filtre partiel, insensible à la casse |
| `author` | `string` | Filtre partiel, insensible à la casse |
| `genre` | `string` | Filtre partiel, insensible à la casse |
| `sort_by` | `string` | Champ de tri : `title`, `author`, `genre`, `published_at`, `created_at` |
| `order` | `asc`/`desc` | Ordre du tri (défaut : `asc`) |
| `skip` | `int` | Pagination — nombre d'éléments à sauter |
| `limit` | `int` | Pagination — nombre d'éléments à retourner |

### Scénario d'utilisation type

```bash
# 1. Créer un utilisateur
POST /users/
{ "name": "Alice", "email": "alice@example.com", "phone": "0600000000", "password": "monMotDePasse" }

# 2. S'authentifier et récupérer un token JWT
POST /auth/login
username=alice@example.com  password=monMotDePasse
→ { "access_token": "eyJ...", "token_type": "bearer" }

# 3. Ajouter un livre
POST /books/
{ "title": "Le Petit Prince", "author": "Saint-Exupéry", "genre": "Littérature" }

# 4. Emprunter le livre (le livre passe à "indisponible")
POST /loans/
{ "user_id": 1, "book_id": 1 }
→ 201 Created, due_date = aujourd'hui + 14 jours

# 5. Tenter de le réemprunter → refus
POST /loans/
→ 400 "Ce livre n'est pas disponible"

# 6. Retourner le livre (le livre redevient "disponible")
POST /loans/1/return

# 7. Consulter l'historique (nécessite le token JWT)
GET /loans/user/1
Authorization: Bearer eyJ...
```

---

## Tests automatisés

Le projet inclut une **suite de 9 tests d'intégration** couvrant les scénarios critiques.

```bash
pytest -v
```

Résultat attendu :

```
tests/test_auth.py::test_login_success          PASSED
tests/test_auth.py::test_login_wrong_password   PASSED
tests/test_books.py::test_create_book           PASSED
tests/test_books.py::test_search_books          PASSED
tests/test_loans.py::test_borrow_book           PASSED
tests/test_loans.py::test_book_unavailable_after_borrow  PASSED
tests/test_loans.py::test_double_borrow_refused PASSED
tests/test_loans.py::test_return_book           PASSED
tests/test_loans.py::test_book_available_after_return    PASSED

9 passed in ~2.3s
```

### Détails de l'infrastructure de test

- Les tests s'exécutent directement sur la **base Oracle de développement** (ou SQLite en CI via `DATABASE_URL_OVERRIDE`).
- Chaque test nettoie ses données en base après exécution (**teardown propre**) pour ne pas polluer les autres tests.
- Les emails de test sont générés avec un **suffixe aléatoire** pour éviter les collisions de contrainte UNIQUE en cas d'échec inattendu.

### CI GitHub Actions

Un pipeline s'exécute automatiquement à chaque push et pull request (`.github/workflows/tests.yml`). Comme Oracle est trop lourd pour la CI, les tests y tournent sur **SQLite** via une variable d'environnement `DATABASE_URL_OVERRIDE` — sans modifier une seule ligne de code applicatif.

---

## Sécurité

| Mesure | Détail |
|--------|--------|
| **Compte Oracle dédié** | L'application utilise `library_app`, jamais le compte `SYSTEM`. Droits limités au strict nécessaire (principe du moindre privilège). |
| **Secrets externalisés** | Identifiants de connexion et clé JWT dans un fichier `.env` non versionné. |
| **Hachage bcrypt** | Les mots de passe sont hachés avec bcrypt (sel unique par utilisateur, facteur de coût 12). Jamais stockés ni renvoyés en clair. |
| **Contrat d'API strict** | Les schémas Pydantic garantissent que le `password_hash` n'est **jamais** exposé dans les réponses de l'API. |
| **Authentification JWT** | Les routes sensibles (ex : historique des emprunts) sont protégées par un token JWT signé (algorithme HS256, expiration configurable). |

---

## Ingestion de données (bonus ETL)

Un script d'ingestion **ETL** peuple la base avec des données de livres réelles, scrapées depuis [books.toscrape.com](https://books.toscrape.com) :

```bash
# Le serveur API doit être lancé au préalable
python scripts/scrape_books.py
```

Le pipeline suit le pattern **Extract – Transform – Load** :

- **Extract** — téléchargement du HTML des pages du catalogue via `requests`
- **Transform** — extraction des données avec `BeautifulSoup`, incluant un **scraping en profondeur** : visite de la page de détail de chaque livre pour récupérer son genre réel depuis le fil d'Ariane
- **Load** — insertion en base via l'API REST (`POST /books/`)

Le script gère l'encodage UTF-8, applique une pause entre les requêtes pour respecter le serveur source, et insère environ **40 livres réels** avec des genres variés (Poetry, Thriller, Music, Travel…).

---

## Persistance des données

Les données sont stockées **de manière permanente** grâce à un **volume Docker** (`oracle-data`) monté sur le répertoire de données d'Oracle :

```yaml
volumes:
  - oracle-data:/opt/oracle/oradata
```

| Action | Données conservées ? |
|--------|:--:|
| Arrêt du serveur uvicorn | ✅ |
| `docker compose stop` / `start` | ✅ |
| `docker compose down` / `up` | ✅ |
| Redémarrage de la machine | ✅ |
| `docker compose down -v` | ❌ (le `-v` détruit le volume) |

Le conteneur est jetable, mais les données lui survivent tant que le volume n'est pas explicitement supprimé.

---

## Auteurs

Projet réalisé en binôme dans le cadre du **MSc Data Engineering — SUPINFO**, module 5BDDD.

- **Rayelen Guesmi**
- **Tharshan Sivapalan**
