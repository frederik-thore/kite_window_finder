# User Story US-001: Task erstellen und abrufen

## Story

Als Teammitglied  
moechte ich eine Aufgabe anlegen und spaeter per ID abrufen koennen,  
damit ich Arbeitspakete im System nachvollziehbar speichern kann.

## Business Value

- Grundlage fuer weiteres Task-Management (Status, Owner, Prioritaet).
- Erste vertikale Scheibe fuer euren Multi-Agenten-Flow (API + Tests + Review).

## Scope

- In Scope:
  - `POST /tasks` zum Erstellen einer Aufgabe.
  - `GET /tasks/{id}` zum Abrufen einer Aufgabe.
  - In-Memory-Speicherung (ohne Datenbank).
- Out of Scope:
  - Update/Delete.
  - Persistenz in DB.
  - Authentifizierung und Autorisierung.

## Akzeptanzkriterien

1. `POST /tasks` akzeptiert JSON mit `title` (Pflicht, nicht leer) und optional `description`.
2. Bei erfolgreichem Erstellen liefert die API `201 Created` und ein Objekt mit `id`, `title`, `description`.
3. `GET /tasks/{id}` liefert bei existierender ID `200 OK` und das gespeicherte Objekt.
4. `GET /tasks/{id}` liefert bei unbekannter ID `404 Not Found`.
5. Ungueltige Eingaben (z. B. leerer `title`) liefern `422 Unprocessable Entity`.
6. Es existieren mindestens:
   - ein positiver Test fuer `POST /tasks`,
   - ein positiver Test fuer `GET /tasks/{id}`,
   - ein negativer Testfall (`404` oder `422`).

## Technische Hinweise

- Neue API-Route unter `app/api/`.
- Business-Logik in `app/services/`.
- Datenmodell in `app/models/`.
- Tests unter `tests/`.

## Definition of Done

- `uv run pytest` ist gruen.
- `uv run ruff check .` ist gruen.
- `uv run ruff format --check .` ist gruen.
- Uebergabe erfolgt im Standardformat aus `AGENTS.md`.
