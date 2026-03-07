# MVP Backlog: Kite Window Finder

## Priorisierung

- `P0`: Blocker-kritisch fuer ein lauffaehiges MVP
- `P1`: Sehr wichtig fuer Produktnutzen, nach P0
- `P2`: Sinnvolle Erweiterung nach MVP-Kern

## P0 Tasks

### T-001 Projekt- und API-Basis aufsetzen

- Prioritaet: `P0`
- Ziel: Solide FastAPI-Struktur mit grundlegenden Endpunkten und Fehlerhandling.
- Deliverables:
  - API-Skeleton unter `app/api`, `app/services`, `app/models`
  - Basisrouting + zentrale Konfiguration
  - Fehlerobjekt fuer 4xx/5xx Responses
- Akzeptanzkriterien:
  - API startet mit `uv run uvicorn app.main:app --reload`
  - `GET /health` liefert `200` mit Status
  - `uv run pytest` laeuft gruen (inkl. Smoke-Test)

### T-002 Spot-Katalog und Spot-Config modellieren

- Prioritaet: `P0`
- Ziel: Alle Spots aus der Projektbeschreibung konfigurierbar machen.
- Deliverables:
  - `Spot`-Modell inkl. `shoreline_bearing_deg`, Windsektoren, Tidefenster
  - Initiale Spotdaten fuer alle 22 Spots
  - Endpoint `GET /spots`
- Akzeptanzkriterien:
  - Alle 22 Spots sind per API abrufbar
  - Jeder Spot hat Mindestfelder fuer Bewertungslogik
  - Validierungsfehler bei unvollstaendiger Spot-Konfiguration

### T-003 Datenprovider-Adapter (Forecast, Marine/Tide, Observations)

- Prioritaet: `P0`
- Ziel: Einheitliche Datenabstraktion fuer mehrere Quellen.
- Deliverables:
  - Adapter-Interface fuer Forecast/Marine/Messdaten
  - Erste Adapter fuer Open-Meteo Forecast + Marine
  - Messdatenadapter fuer Meteostat
- Akzeptanzkriterien:
  - Ein Spot + Zeitfenster kann aus allen 3 Datentypen geladen werden
  - Fehler/Fallbacks liefern klare Fehlermeldungen
  - Unit-Tests fuer Adapter-Mapping vorhanden

### T-004 Bewertungsengine v2 implementieren

- Prioritaet: `P0`
- Ziel: 0-5 Sterne Score mit harten Gates und Teil-Scores.
- Deliverables:
  - Bewertungsservice mit `S_wind`, `S_dir`, `S_tide`, `S_thermal`, `S_spot`
  - Harte Regeln (`offshore`, `<10 kn`, `kein Tageslicht` => `0`)
  - Halbsterne-Rundung
- Akzeptanzkriterien:
  - `GET /spots/{id}/rating?date=YYYY-MM-DD` liefert Stundenrating
  - Testfaelle fuer harte Gates und Grenzwerte sind gruen
  - `GET /spots/{id}/explain?timestamp=...` erklaert den Score nachvollziehbar

### T-005 7-Tage-Zeitfenster und Timeseries-Endpoint

- Prioritaet: `P0`
- Ziel: Nutzer koennen Rueckblick/Heute/Vorschau direkt abrufen.
- Deliverables:
  - Endpoint `GET /spots/{id}/timeseries?from=...&to=...`
  - Standardzeitfenster `-3 bis +3 Tage` relativ zu heute
  - Serverseitige Zeitzonenbehandlung pro Spot
- Akzeptanzkriterien:
  - Ergebnis enthaelt alle Stundenpunkte im Fenster
  - Tagesgrenzen sind fuer Spot-Zeitzone korrekt
  - Integrationstests fuer Zeitfenster vorhanden

### T-006 Minimal-Frontend (Map, Day Picker, Stundenrating)

- Prioritaet: `P0`
- Ziel: Nutzbares MVP-UI fuer Kernerlebnis.
- Deliverables:
  - Weltkarte mit Spot-Markern
  - Tagesauswahl fuer 7 Tage
  - Stundenliste/Timeline mit Sternen
- Akzeptanzkriterien:
  - Spotauswahl + Tageswechsel aktualisiert Ratings
  - Ratings und Kernparameter sind sichtbar
  - Responsive Nutzung auf Desktop und Mobile

## P1 Tasks

### T-007 Forecast-vs-Messdaten Korrelation und Modellwahl

- Prioritaet: `P1`
- Ziel: Je Spot den besten Forecast automatisiert waehlen.
- Deliverables:
  - Berechnung `MAE_wind_kn`, `MAE_dir_deg`, `kiteable_hit_rate`
  - `model_skill` nach definierter Gewichtung
  - Endpoint `GET /spots/{id}/model-skill?window=30d`
- Akzeptanzkriterien:
  - Skill-Werte fuer Spot abrufbar
  - Aktives Modell je Spot eindeutig markiert
  - Rechenlogik durch Tests abgesichert

### T-008 UI fuer Korrelation und Modelltransparenz

- Prioritaet: `P1`
- Ziel: Modellentscheidung fuer Nutzer sichtbar machen.
- Deliverables:
  - Chart Forecast vs Messdaten (30 Tage)
  - Anzeige aktives Modell + Fehlerkennzahlen
  - Modellwechselhistorie
- Akzeptanzkriterien:
  - Nutzer sehen Kennzahlen ohne Entwicklerwissen
  - Chart zeigt Datenkonsistenz mit Backend-Endpunkten
  - Leere Datenfaelle werden sauber behandelt

### T-009 Manuelle Forecast-Anpassung (Wind Offset)

- Prioritaet: `P1`
- Ziel: Forecast manuell korrigieren und Sterne live aktualisieren.
- Deliverables:
  - Endpoint `POST /spots/{id}/adjustments`
  - UI-Regler fuer Windstaerke- und Richtungs-Offset
  - Delta-Anzeige vor/nach Anpassung
- Akzeptanzkriterien:
  - Anpassung wirkt sofort auf Stundenratings
  - Anpassung wird protokolliert und abrufbar
  - Ruecksetzen auf Standard moeglich

### T-010 Konservative Neoprenempfehlung integrieren

- Prioritaet: `P1`
- Ziel: Praxistaugliche Kleidungsempfehlung je Stunde.
- Deliverables:
  - Service fuer Empfehlung auf Basis Wasser/Luft/Wind/Strahlung
  - UI-Hinweis in der Stunden-Detailansicht
- Akzeptanzkriterien:
  - Regeln aus `projektbeschreibung.md` abgebildet
  - Wind- und Strahlungseinfluss nachvollziehbar
  - Tests fuer typische Klimaszenarien vorhanden

## P2 Tasks

### T-011 Spot-spezifische Feintuning-Regeln

- Prioritaet: `P2`
- Ziel: Qualitaet je Spot durch lokale Regeln verbessern.
- Deliverables:
  - Spot-Overrides fuer Tiefe/Stroemung/Startzone
  - Versionierte Spot-Regeldatei
- Akzeptanzkriterien:
  - Overrides beeinflussen nur den jeweiligen Spot
  - Aenderungen sind auditierbar

### T-012 Betriebsautomatisierung und Re-Kalibrierung

- Prioritaet: `P2`
- Ziel: Stabiler Betrieb mit automatischer Modellpflege.
- Deliverables:
  - Geplanter Job fuer taegliche Re-Kalibrierung
  - Auto-Switch-Regel (7 Tage stabil besser)
  - Monitoring/Alerts fuer fehlende Daten
- Akzeptanzkriterien:
  - Joblaeufe sind nachvollziehbar geloggt
  - Auto-Switch tritt nur bei Regelkonformitaet ein
  - Ausfall einzelner Quellen fuehrt nicht zu App-Abbruch

## Empfohlene Umsetzungsreihenfolge

1. `T-001` bis `T-006` (MVP Kern lauffaehig)
2. `T-007` bis `T-010` (Qualitaet + Transparenz + Praxisnutzen)
3. `T-011` bis `T-012` (Feinschliff + Betriebsstabilitaet)

## Exit-Kriterien fuer MVP Release

- Alle `P0` Tasks abgeschlossen
- Mindestens `T-007` und `T-009` aus `P1` abgeschlossen
- `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` sind gruen
- Bewertungslogik liefert fuer Kernspots plausible Ergebnisse
