# Kurzbericht: Forecast-Korrelation und Modellwahl je Spot

## 1. Ziel

Je Spot wird nicht pauschal ein Forecast verwendet, sondern das historisch verlaesslichste Modell auf Basis realer Messdaten naher Stationen.

## 2. Bewertungsmetriken

- `MAE_wind_kn`: mittlerer absoluter Fehler der Windstaerke
- `MAE_dir_deg`: mittlere absolute Windrichtungsabweichung
- `kiteable_hit_rate`: Trefferquote fuer "kitebar" vs. "nicht kitebar" gemaess Spotregeln

## 3. Gewichtete Modellwertung (Vorschlag)

`model_skill = 0.50*(1-norm(MAE_wind_kn)) + 0.30*(1-norm(MAE_dir_deg)) + 0.20*(kiteable_hit_rate)`

Rolling Window: letzte 30 Tage.

## 4. Initiale Modellstrategie nach Regionen

- Nord-/Ostsee (Hvide Sande, Fehmarn):
  - ICON + ECMWF vergleichen, stationsnah bestes Modell waehlen
- Atlantik Europa/Nordafrika (Tarifa, Essaouira, Dakhla, Sal):
  - ECMWF + GFS vergleichen
- Mittelmeer/Rotes Meer (Sicily, Sardinia, Kos, Djerba, El Gouna, Seahorse Bay):
  - ECMWF + ICON vergleichen
- Tropen/Passat (Kalpitiya, Jambiani, Mwazaro, Brazil-Spots, Punta Chame):
  - GFS + ECMWF vergleichen
- Suedafrika (Cape Town):
  - ECMWF + GFS, Kuestenstationen priorisieren

## 5. Datenquellenmix (MVP)

- Forecast: Open-Meteo Forecast (mehrere Modelle)
- Marine/Tide: Open-Meteo Marine, optional WorldTides
- Messdaten: Meteostat, optional NDBC

## 6. Modellwechsel-Regeln

- Taegliche Re-Kalibrierung der Skill-Werte
- Auto-Switch nur wenn neues Modell mindestens 7 Tage stabil besser ist
- Bei instabilen Ergebnissen bleibt aktives Modell fix
- Manuelle Uebersteuerung bleibt moeglich und wird geloggt

## 7. Darstellung in der App

Pro Spot:
- aktives Modell und letzte Aktualisierung
- 30-Tage Forecast-vs-Messdaten-Chart
- Skill-Kennzahlen (`MAE_wind_kn`, `MAE_dir_deg`, `kiteable_hit_rate`)
- Delta nach manuellem Wind-Offset
- Historie der Modellwechsel

## 8. Offene Feinjustierung

- Normalisierung der Fehler fuer verschiedene Klimazonen
- Stationsgewichtung bei mehreren nahen Messpunkten
- Mindestdatenmenge vor automatischem Modellwechsel
