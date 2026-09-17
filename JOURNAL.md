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