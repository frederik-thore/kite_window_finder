# codex_multi_agent backend starter

Minimal FastAPI starter structure for a multi-agent pilot setup.

## Structure

- `app/api/`: API routes
- `app/services/`: business logic
- `app/models/`: data models
- `tests/`: tests

## Quickstart

```bash
uv venv
source .venv/bin/activate
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

## Checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

## uv workflow

```bash
# Sync dependencies from pyproject.toml
uv sync --extra dev

# Run app
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest -q
```

Open:
- API docs: `http://127.0.0.1:8000/docs`
- Web app: `http://127.0.0.1:8000/app`

## Live data providers

Default is live data. Synthetic fallback is disabled by default.

Primary sources:
- Forecast: Open-Meteo weather API (model-specific endpoints: ECMWF/GFS/ICON)
- Marine/Tide/Water temperature: Open-Meteo marine API
- Observations: Meteostat (if API key provided), otherwise Open-Meteo archive

Update behavior:
- Provider cache TTL defaults to 15 minutes (`PROVIDER_CACHE_TTL_SECONDS=900`)
- Data is requested fresh after cache expiry (hourly-scale updates)

Environment:

```bash
export LIVE_WEATHER_ENABLED=true
export ALLOW_SYNTHETIC_FALLBACK=false
```

Optional Meteostat observations (if you have a RapidAPI key):

```bash
export METEOSTAT_API_KEY=your_key
export METEOSTAT_API_HOST=meteostat.p.rapidapi.com
```

Supported time windows in API/UI:
- Past: up to 7 days
- Future: up to 3 days

## GitHub Pages

This project can be deployed quickly in a split setup:

- Frontend: GitHub Pages from `frontend/`
- Backend API: separate FastAPI host such as Render, Railway, Fly.io, or a VPS

GitHub Pages cannot run the Python backend itself.

Frontend config:

- edit [frontend/config.js](/Users/frederikberger/repositories/codex_multi_agent/frontend/config.js)
- set `API_BASE_URL` to your deployed backend, for example:

```js
window.APP_CONFIG = {
  API_BASE_URL: "https://your-backend.example.com",
};
```

Backend CORS:

```bash
export CORS_ALLOW_ORIGINS="https://<user>.github.io"
```

You can also allow multiple origins comma-separated.

## Deploy Ablauf

Empfohlener schneller Setup:

1. Backend auf Render deployen
2. die Render-URL in [frontend/config.js](/Users/frederikberger/repositories/codex_multi_agent/frontend/config.js) eintragen
3. Frontend ueber GitHub Pages deployen
4. `CORS_ALLOW_ORIGINS` im Backend auf die finale GitHub-Pages-URL setzen

### 1. Backend auf Render

Datei dafuer liegt schon bereit:
- [render.yaml](/Users/frederikberger/repositories/codex_multi_agent/render.yaml)

Render-Konfiguration:
- Build Command: `pip install .`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- notwendige Env Vars:
  - `LIVE_WEATHER_ENABLED=true`
  - `ALLOW_SYNTHETIC_FALLBACK=false`
  - `CORS_ALLOW_ORIGINS=https://<dein-user>.github.io`

Optional:
- `METEOSTAT_API_KEY=...`
- `METEOSTAT_API_HOST=meteostat.p.rapidapi.com`

### 2. Frontend-API eintragen

In [frontend/config.js](/Users/frederikberger/repositories/codex_multi_agent/frontend/config.js):

```js
window.APP_CONFIG = {
  API_BASE_URL: "https://dein-render-service.onrender.com",
};
```

### 3. GitHub Pages

Workflow ist schon vorbereitet:
- [.github/workflows/deploy-pages.yml](/Users/frederikberger/repositories/codex_multi_agent/.github/workflows/deploy-pages.yml)

Voraussetzung im GitHub-Repo:
- `Settings -> Pages -> Build and deployment -> Source = GitHub Actions`

Dann reicht ein Push auf `main`.

### 4. Final pruefen

Nach dem Deploy:
- Frontend oeffnen: `https://<dein-user>.github.io/<repo-name>/`
- pruefen, ob `/spots` geladen wird
- pruefen, ob fuer `Seahorse Bay` und morgen ein Forecast erscheint

## Empfohlene Push-Reihenfolge

1. Repo nach GitHub pushen
2. Render-Service anlegen
3. Render-URL in `frontend/config.js` eintragen
4. nochmal nach GitHub pushen
5. GitHub Pages oeffnen
