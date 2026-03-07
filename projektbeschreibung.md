# Projektbeschreibung: Kite Window Finder

## 1. Produktziel

Die Webapp bewertet fuer jeden Spot und jede Stunde eines Tages, wie gut die Kite-Bedingungen sind (0 bis 5 Sterne), und zeigt den besten Kite-Zeitpunkt klar an.

## 2. Kernfunktionen

- Spot-Auswahl per Weltkarte und Spotliste
- Tagesauswahl: 3 Tage Vergangenheit, heute, 3 Tage Zukunft
- Stundenansicht mit 0-5 Sterne Rating
- Anzeige von Wind, Richtung, Tide, Wetter, Luft-/Wassertemperatur, Tageslicht
- Manuelle Forecast-Anpassung (Windstaerke/Windrichtung)
- Historische Forecast-vs-Messdaten-Korrelation pro Spot

## 3. Spot-Katalog (aus deinem Foto)

- Denmark | Hvide Sande
- Germany | Fehmarn
- Italy | Sicily
- Morocco | Essaouira
- Morocco | Dakhla
- Spain | Tarifa
- Spain | Fuerteventura
- Sardinia | Kite2Sail
- Greece | Kos
- Egypt | El Gouna
- Egypt | Seahorse Bay
- Tunisia | Djerba
- Cape Verde | Sal
- Brazil | Tatajuba
- Brazil | Prea
- Brazil | Jericoacoara
- Brazil | Kite Safari
- Panama | Punta Chame
- Zanzibar | Jambiani
- Kenya | Mwazaro Beach
- South Africa | Cape Town
- Sri Lanka | Kalpitiya

## 4. Finale Bewertungsformel v2 (Vorschlag)

### 4.1 Harte Ausschlussregeln

Wenn eine dieser Bedingungen zutrifft, ist das Ergebnis direkt `0 Sterne`:

- Wind ist ablandig oder cross-offshore
- Windgeschwindigkeit ist kleiner als `10 kn`
- Kein Tageslicht

### 4.2 Teil-Scores (0.0 bis 1.0)

- `S_wind`: Windstaerke
- `S_dir`: Windrichtung relativ zur Shoreline
- `S_tide`: Tidenfenster je Spot
- `S_thermal`: thermischer Komfort (Wasser, Luft, Wind, Strahlung)
- `S_spot`: spot-spezifische Faktoren (Tiefe, Chop, Stroemung)

### 4.3 Gewichtung

- Windstaerke: `30%`
- Windrichtung: `25%`
- Tide: `20%`
- Thermal/Komfort: `20%`
- Spotfaktor: `5%`

Formel:

`score = 0.30*S_wind + 0.25*S_dir + 0.20*S_tide + 0.20*S_thermal + 0.05*S_spot`

`stars = round_to_0.5(5 * score)`

### 4.4 Start-Schwellenwerte (Vorschlag)

- `S_wind`:
  - 10-12 kn: 0.60
  - 12-16 kn: 0.85
  - 16-24 kn: 1.00
  - 24-30 kn: 0.70
  - >30 kn: 0.40
- `S_dir`:
  - side-shore: 1.00
  - side-onshore: 0.90
  - onshore: 0.75
  - offshore/cross-offshore: 0.00 (Gate)

## 5. Konservative Neoprenempfehlung v2

Die Empfehlung basiert nicht nur auf Wassertemperatur, sondern auch auf Wind und Sonneneinstrahlung.

### 5.1 Basis nach Wassertemperatur

- >24C: 2/2 oder Shorty
- 20-24C: 3/2
- 16-20C: 4/3
- 12-16C: 5/4
- <=12C: 6/5+

### 5.2 Korrekturregeln (jeweils +1 Stufe dicker)

- Wind >=18 kn
- Geringe Strahlung (`shortwave_radiation < 250 W/m2`)
- Lufttemperatur <20C

Deckelung: minimal 2/2, maximal 6/5+.

Hinweis fuer warmes Wasser mit starkem Wind (wie von dir beschrieben in Hurghada):
- Trotz hoher Wassertemperatur kann ein 4/3 sinnvoll sein.

## 6. Spot-Konfiguration (pro Spot zu definieren)

Pro Spot werden mindestens folgende Felder gepflegt:

- `id`, `name`, `lat`, `lon`
- `shoreline_bearing_deg`
- `offshore_sector_deg` (hartes 0-Sterne-Gate)
- `preferred_wind_sector_deg`
- `tide_windows` (optimal/ok/schlecht)
- `depth_profile` (flach/mittel/tief)
- `spot_notes` (z. B. Starkstroemung, Start-/Landesituation)
- `station_candidates` (Messstationen mit Distanzgewicht)

## 7. Datenquellen-Set (Vorschlag)

- Forecast:
  - Open-Meteo Forecast (mehrere Modelle je Spot)
- Marine/Tide/Sea:
  - Open-Meteo Marine
  - optional WorldTides als Praezisionsquelle
- Messdaten:
  - Meteostat (nahe Stationen)
  - optional NDBC Buoys (wo verfuegbar)
- Tageslicht:
  - Sunrise/Sunset aus Wetterquelle oder Astronomie-Endpunkt

## 8. Datenmodell und API-Vertraege

### 8.1 Kernentitaeten

- `Spot`
- `ForecastPoint`
- `ObservationPoint`
- `RatingPoint`
- `ForecastModelSkill`
- `UserAdjustment`

### 8.2 MVP-Endpunkte

- `GET /spots`
- `GET /spots/{id}/rating?date=YYYY-MM-DD`
- `GET /spots/{id}/timeseries?from=...&to=...`
- `GET /spots/{id}/model-skill?window=30d`
- `POST /spots/{id}/adjustments`
- `GET /spots/{id}/explain?timestamp=...` (Begruendung der Sterne)

## 9. MVP-UI-Flow

1. Spot auf Karte oder in Liste waehlen
2. Tag im 7-Tage-Fenster waehlen
3. Stunden-Timeline mit Sternen lesen
4. Detailansicht je Stunde oeffnen
5. Forecast-vs-Messdaten-Karteireiter pruefen
6. Optional Forecast-Offset setzen und Auswirkungen sofort sehen

## 10. Betriebsregeln

- Forecast-Ingest: stuendlich
- Messdaten-Ingest: alle 10-30 Minuten (quellenabhaengig)
- Modellguete pro Spot neu berechnen: taeglich, Rolling Window 30 Tage
- Automatische Modellumschaltung nur bei stabil besserem Modell (z. B. 7 Tage in Folge)
- Alle Sternewerte muessen via `explain` nachvollziehbar sein

## 11. MVP-In Scope

- Alle Spots aus dem Katalog als auswaehlbare Spots
- Stunden-Rating 0-5 Sterne mit harter Gate-Logik
- Anzeige von Forecast + Messdaten + Korrelation
- Manuelle Forecast-Anpassung in der UI
- Cleanes UI im Apple/Google-inspirierten Stil

## 12. Out of Scope (MVP)

- Accounts/Login
- Push-Benachrichtigungen
- Social-/Community-Features
- ML-Personalisierung
- Vollstaendige Buchungs- oder Reisefunktionen
