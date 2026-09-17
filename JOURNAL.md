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