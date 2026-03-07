# Multi-Agent Pilot Setup

Dieses Dokument definiert ein pragmatisches Rollenmodell fuer ein erstes Multi-Agenten-Softwareprojekt mit Python-Backend (Web-App mit CRUD + Auth als Beispiel).

## Pilotziel

In 1-2 Tagen validieren, ob ein Multi-Agenten-Ansatz schneller und robuster liefert als ein einzelner Generalist-Agent.

## Rollen

### 1) Orchestrator (Planner)

- **Mission:** Zerlegt Features in Arbeitspakete, priorisiert und delegiert.
- **Input:** Projektziel, Backlog, Architekturregeln, bekannte Risiken.
- **Output:** Task-Plan, Reihenfolge, klare Akzeptanzkriterien pro Task.
- **Darf:** Aufgaben zuschneiden, Abhaengigkeiten umplanen, Blocker eskalieren.
- **Darf nicht:** Produktiven Code direkt aendern.
- **Done:** Jeder Task ist klar beschrieben, einem Agenten zugewiesen und hat Abnahmekriterien.

### 2) Implementation Agent (Python Backend + Frontend)

- **Mission:** Implementiert Features gemaess Task-Plan, mit Fokus auf Python-Backend.
- **Input:** Konkreter Task inkl. Akzeptanzkriterien und betroffene Module.
- **Output:** Code-Patch, technische Aenderungsnotiz, API-Aenderungen dokumentiert.
- **Darf:** Betroffenen Code aendern, kleine lokale Refactorings, Typen ergaenzen.
- **Darf nicht:** Architekturprinzipien, API-Contracts oder Datenmodell ohne Freigabe brechen.
- **Done:** Backend-Checks gruen (`ruff`, `pytest`), Task-Akzeptanzkriterien erfuellt.

### 3) QA/Test Agent

- **Mission:** Schreibt/erweitert Tests, validiert Regressionen.
- **Input:** Implementierungs-Patch, Anforderungen, vorhandene Teststrategie.
- **Output:** Testreport (Pass/Fail), reproduzierbare Bug-Beschreibungen.
- **Darf:** Testcode anpassen, Findings priorisieren.
- **Darf nicht:** Feature-Logik stillschweigend reparieren statt zurueckzugeben.
- **Done:** Relevante Tests fuer neuen Scope vorhanden und Risiken dokumentiert.

### 4) Review/Security Agent

- **Mission:** Fuehrt finales Qualitaets- und Sicherheits-Gate durch.
- **Input:** Patch + Testreport + Akzeptanzkriterien.
- **Output:** Entscheidung `approve` oder `changes_requested` mit Begruendung.
- **Darf:** Kritische Findings blockieren.
- **Darf nicht:** Scope im Gate erweitern ("nice to have").
- **Done:** Klare Go/No-Go-Entscheidung inkl. priorisierter Findings.

## Einheitliches Uebergabeformat

Jede Agenten-Uebergabe nutzt exakt dieses Schema:

```md
### Kontext
- Task-ID:
- Ziel:
- Betroffene Dateien/Module:

### Ergebnis
- Was wurde gemacht:
- Was wurde bewusst nicht gemacht:

### Qualitaet
- Checks/Tests:
- Offene Risiken:

### Naechster Schritt
- Empfaenger-Agent:
- Konkrete Aktion:
```

## Prozess (Minimal-Workflow)

1. Orchestrator erstellt 3-6 kleine Tasks.
2. Implementation Agent setzt Task fuer Task um.
3. QA/Test Agent prueft jeden abgeschlossenen Task.
4. Review/Security Agent gate-t jede Lieferung.
5. Orchestrator tracked Status und priorisiert laufend nach.

## Startregeln

- Tasks klein halten (max. 2-4 Stunden pro Task).
- Ein Agent pro Verantwortungsbereich.
- Keine Uebergabe ohne Standardformat.
- Keine stillen Scope-Erweiterungen waehrend der Umsetzung.
- Blocker immer mit konkretem naechsten Entscheidungspunkt eskalieren.

## Stackvorgaben (Python Backend)

- Bevorzugtes API-Framework: FastAPI.
- Python-Version: 3.11+.
- Validierung/Schemas: Pydantic.
- Lint/Format: `ruff check` und `ruff format`.
- Tests: `pytest` mit Fokus auf Service- und API-Tests.
- Projektstruktur fuer Backend-Tasks:
  - `app/api/` fuer Endpoints
  - `app/services/` fuer Business-Logik
  - `app/models/` fuer Datenmodelle
  - `tests/` fuer Unit- und Integrationstests

## Definition of Done fuer Backend-Tasks

- API-Contract angepasst und in der Uebergabe genannt.
- Fehlerfaelle und Validierung sind getestet.
- Mindestens ein positiver und ein negativer Testfall pro neuem Endpoint.
- `ruff check`, `ruff format --check` und `pytest` laufen erfolgreich.

## Task-Template fuer den Orchestrator

```md
## Task: <ID + Titel>

### Ziel
<Ein Satz mit fachlichem Ergebnis>

### Akzeptanzkriterien
- [ ] ...
- [ ] ...

### Scope
- In Scope: ...
- Out of Scope: ...

### Technische Hinweise
- Betroffene Dateien/Module:
- Risiken/Abhaengigkeiten:

### Zuweisung
- Primaer-Agent:
- Nachgelagerter Agent:
```
