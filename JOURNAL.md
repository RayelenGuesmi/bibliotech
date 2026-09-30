# Journal de bord — Système de gestion de bibliothèque

Projet 5BDDD — API de gestion de bibliothèque (Oracle + FastAPI)
Auteur : Rayelen · SUPINFO MSc

---

## Phase 0 — Setup de l'environnement
**Date : 17/09/2026**

- Création du dépôt `mini_projet_librairie`.
- Mise en place d'Oracle Database Free 23 (26ai) via Docker (`docker-compose.yml`).
- Base `FREEPDB1` opérationnelle sur le port 1521, volume persistant configuré.
- Vérification : `DATABASE IS READY TO USE!`

## Phase 1 — Sécurisation de la base
**Date : 17/09/2026**

- Application du principe du **moindre privilège** : création d'un compte
  applicatif dédié `library_app` distinct du compte admin `SYSTEM`.
- Droits accordés strictement nécessaires : `CREATE SESSION`, `CREATE TABLE`,
  `CREATE SEQUENCE`, `CREATE VIEW`, quota sur le tablespace `USERS`.
- Aucun privilège DBA accordé à l'application.

## Phase 2 — Environnement Python & connexion
**Date : 17/09/2026**

- Environnement virtuel Python 3.12 (`venv`).
- Installation des dépendances (FastAPI, SQLAlchemy, Alembic, oracledb, Pydantic…).
- Configuration de la connexion via variables d'environnement (`.env` + Pydantic Settings),
  aucun secret en dur dans le code.
- Couche d'accès BDD : moteur SQLAlchemy + session par requête (`get_db`).
- Test de bout en bout Python → Oracle réussi.

## Phase 3 — Modèles de données (SQLAlchemy)
**Date : 17/09/2026**

- Modélisation de 3 entités : `User`, `Book`, `Loan`.
- `Loan` conçue comme table d'association portant les infos d'emprunt (dates, statut).
- Relations bidirectionnelles (`relationship` / `back_populates`).
- Contraintes d'intégrité : clés primaires, `email` unique, clés étrangères, champs obligatoires.

## Phase 4 — Migrations (Alembic)
**Date : 17/09/2026**

- Initialisation d'Alembic, branchement sur la config `.env` et les métadonnées SQLAlchemy.
- Génération de la migration initiale par autogenerate.
- Application à Oracle : tables `USERS`, `BOOKS`, `LOANS` + `ALEMBIC_VERSION` créées.
- Schéma désormais versionné et reproductible.

## Phase 5 — API REST des livres (Pydantic + FastAPI)
**Date : 17/09/2026**

- Schémas Pydantic (Create / Read / Update) pour séparer le contrat d'API du modèle BDD.
- Couche CRUD isolant l'accès aux données des routes.
- Routeur FastAPI : 5 routes REST (POST, GET liste, GET détail, PUT, DELETE) pour les livres.
- Documentation Swagger générée automatiquement sur /docs.
- **Difficulté rencontrée & résolue** : Oracle n'auto-incrémente pas les clés
  primaires comme Postgres. Correction via colonnes `Identity()` sur les modèles,
  puis régénération de la migration Alembic. Insertion validée (201 Created).


## Phase 6 — Gestion des utilisateurs & sécurité des mots de passe
**Date : 17/09/2026**

- Schémas Pydantic séparant l'entrée (avec mot de passe) de la sortie (sans mot de passe ni hash).
- Validation du format email via `EmailStr`.
- Hashage bcrypt (sel unique par mot de passe, facteur de coût 12) : mot de passe jamais stocké en clair.
- Règle métier : refus d'un email déjà enregistré.
- **Difficulté résolue** : incompatibilité passlib / bcrypt 5.0 → passage à la bibliothèque `bcrypt` en direct.


## Phase 7 — Gestion des emprunts (logique métier)
**Date : 17/09/2026**

- Règle centrale : un livre ne peut être emprunté que s'il est disponible ; l'emprunt le rend indisponible.
- Retour : marque l'emprunt rendu (date + statut) et rend le livre à nouveau disponible.
- Protections : livre/utilisateur inexistant, livre indisponible, double retour — traduits en erreurs HTTP 400 explicites.
- Atomicité : emprunt + changement de disponibilité dans une seule transaction.
- Historique des emprunts par utilisateur.
- Scénario complet validé de bout en bout via Swagger.

## Phase 8 — Recherche de livres (titre, auteur, genre)
**Date : 29/09/2026**

- Ajout de la fonction CRUD `search_books` : filtrage dynamique par `title`,`author` et `genre`, chaque critère étant optionnel et cumulable.
- Recherche partielle et insensible à la casse via `ilike` (traduit correctement en `LOWER(...) LIKE LOWER(...)` sous Oracle par SQLAlchemy).
- Intégration directe dans la route `GET /books/` existante (plutôt qu'une route séparée), avec conservation de la pagination `skip`/`limit`.
- Validation manuelle via `curl` : filtre par genre (`?genre=Poetry`),par auteur (`?author=baudelaire`), par titre partiel (`?title=fleurs`),casse différente testée avec succès, et cas sans résultat vérifié (`?genre=Fiction` → liste vide).

## Phase 9 — Authentification JWT
**Date : 29/09/2026**

- Ajout de `create_access_token` et `get_current_user` dans `security.py` (encodage/décodage JWT via `python-jose`, algorithme HS256).
- Clé secrète et durée d'expiration ajoutées à `Settings` (`.env`, jamais en dur dans le code).
- Nouvelle route `POST /auth/login` (`OAuth2PasswordRequestForm`) : vérifie l'email et le mot de passe hashé, renvoie un token en cas de succès, `401` sinon.
- Validation manuelle via `curl` : login réussi avec token renvoyé, échec correctement rejeté avec mauvais mot de passe.

## Phase 10 — Protection d'une route par JWT
**Date : 29/09/2026**

- Route `GET /loans/user/{user_id}` protégée via `Depends(get_current_user)`.
- Validation manuelle : requête sans token → 401 "Not authenticated", equête avec token valide (obtenu via `/auth/login`) → 200, liste des emprunts renvoyée.

## Phase 11 — Tests automatisés (pytest)
**Date : 29/09/2026**

- Mise en place de `pytest` + `httpx` (TestClient FastAPI), exécutés directement sur la base Oracle de dev.
- Fixtures avec teardown (`tests/conftest.py`) : chaque livre/utilisateur/emprunt créé pour un test est supprimé en base après exécution, pour ne pas polluer les données. Emails générés avec suffixe aléatoire pour éviter les collisions en cas d'échec avant nettoyage.
- 9 tests couvrant : création/recherche de livres, login (succès/échec), emprunt (rend le livre indisponible), double emprunt refusé (400), retour (rend le livre disponible).
- **Difficulté résolue** : `ModuleNotFoundError: No module named 'app'` lors de l'exécution de pytest — ajout d'un `pytest.ini` avec `pythonpath = .` pour forcer la racine du projet dans le chemin Python.
- Résultat : `9 passed` en ~2.3s.

## Phase 12 — Nettoyage des warnings de dépréciation
**Date : 29/09/2026**

- Ajout d'une fonction utilitaire `utcnow()` centralisée dans `database.py`(basée sur `datetime.now(timezone.utc).replace(tzinfo=None)`), remplaçant `datetime.utcnow` (déprécié) dans les modèles `User`, `Book`, `Loan`.
- Installation de `httpx2`, supporté nativement par le TestClient de Starlette, supprimant le `StarletteDeprecationWarning` lié à `httpx`.
- Résultat : `pytest -v` passe de 17 warnings à 0, sans régression (9 tests toujours PASSED).

## Phase 13 — Pagination et tri des livres
**Date : 29/09/2026**

- Ajout des paramètres `sort_by` et `order` (asc/desc) à `search_books` et à la route `GET /books/`.
- Tri restreint à une liste blanche de champs autorisés (`title`, `author`,`genre`, `published_at`, `created_at`) pour éviter toute exposition de champ sensible ou erreur serveur sur un nom de colonne invalide.
- **Difficulté résolue** : doublon accidentel de la route `GET /books/` dans `routers/books.py` (ancienne version sans tri restée dans le fichier après l'ajout de la nouvelle) — FastAPI utilisait la première définition trouvée, rendant le tri invisible malgré un code correct. Suppression de la définition dupliquée.
- Validation manuelle via `curl` : tri croissant/décroissant par titre vérifié avec deux livres, champ de tri invalide correctement rejeté (400).

## Phase 14 — Gestion des retards d'emprunt
**Date : 29/09/2026**

- Ajout du champ `due_date` au modèle `Loan`, calculé à l'emprunt (`loan_date` + 14 jours).
- Nouvelle route `GET /loans/overdue` : liste les emprunts non rendus dont la `due_date` est dépassée.
- **Difficulté résolue** : la première migration autogenerate est sortie vide (`pass`) car le modèle n'avait pas encore été modifié au moment de la génération — annulée et régénérée après correction du modèle. La colonne `due_date` étant `NOT NULL` alors que des emprunts existaient déjà en base, la migration a été adaptée en 3 temps : ajout de la colonne en nullable, backfill via `UPDATE ... loan_date + INTERVAL '14' DAY`, puis passage en `NOT NULL`.
- Validation manuelle : `due_date` correctement calculée à la création (loan_date + 14 jours) ; retard simulé en base (SQL direct) puis vérifié correctement détecté par `/loans/overdue`.

## Phase 15 — CI GitHub Actions
**Date : 29/09/2026**

- Ajout de `.github/workflows/tests.yml` : lance `pytest` à chaque push ou pull request.
- Défi résolu : Oracle trop lourd pour tourner facilement en CI → ajout d'un `database_url_override` optionnel dans `Settings` (`app/config.py`),permettant de basculer vers SQLite via une variable d'environnement sans toucher à la config Oracle habituelle.
- Migration `due_date` rendue portable Oracle/SQLite : détection du dialecte (`bind.dialect.name`) pour adapter la syntaxe de backfill (`INTERVAL` Oracle vs `datetime()` SQLite), et utilisation du mode batch d'Alembic pour la contrainte `NOT NULL` (SQLite ne supporte pas `ALTER COLUMN` directement).
- **Difficulté résolue** : `requirements.txt` contenait deux paquets fusionnés par erreur (`beautifulsoup4pytest` au lieu de deux lignes séparées), causant l'échec du premier run CI. Corrigé.
- Résultat : badge OK passing sur GitHub Actions, run complet en ~20-27s.


## Bonus — Ingestion de données par scraping (ETL)
**Date : 17/09/2026**

- Script d'ingestion `scripts/scrape_books.py` alimentant la base via l'API (POST /books/).
- Pattern ETL : EXTRACT (HTML via requests) → TRANSFORM (parsing BeautifulSoup) → LOAD (POST API).
- Scraping en profondeur : visite de la page de détail de chaque livre pour extraire son vrai genre (breadcrumb).
- Difficultés rencontrées & résolues : encodage UTF-8 mal deviné (£ → Â£), respect du serveur (pause entre requêtes), gestion des catégories génériques du site source.
- Résultat : ~40 livres réels avec genres variés (Poetry, Thriller, Music, Travel…).

