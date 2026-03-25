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
- Forecast cache can be configured separately (`FORECAST_PROVIDER_CACHE_TTL_SECONDS`)
- Observation cache can be configured separately (`OBSERVATION_PROVIDER_CACHE_TTL_SECONDS`)
- Default fallback TTL remains 15 minutes (`PROVIDER_CACHE_TTL_SECONDS=900`)
- For low API call volume in production, use:
  - `FORECAST_PROVIDER_CACHE_TTL_SECONDS=86400` (24h)
  - `OBSERVATION_PROVIDER_CACHE_TTL_SECONDS=1800` (30 min)

Environment:

```bash
export LIVE_WEATHER_ENABLED=true
export ALLOW_SYNTHETIC_FALLBACK=false
export FORECAST_PROVIDER_CACHE_TTL_SECONDS=86400
export OBSERVATION_PROVIDER_CACHE_TTL_SECONDS=1800
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

1. Backend auf Hostinger VPS deployen
2. die VPS-API-URL in [frontend/config.js](/Users/frederikberger/repositories/codex_multi_agent/frontend/config.js) eintragen
3. Frontend ueber GitHub Pages deployen
4. `CORS_ALLOW_ORIGINS` im Backend auf die finale GitHub-Pages-URL setzen

### 1. Backend auf Hostinger VPS

Deployment-Dateien:
- [setup_hostinger_vps.sh](/Users/frederikberger/repositories/codex_multi_agent/deploy/setup_hostinger_vps.sh)
- [kite-window-finder-api.service](/Users/frederikberger/repositories/codex_multi_agent/deploy/systemd/kite-window-finder-api.service)
- [kite-window-finder-api.conf](/Users/frederikberger/repositories/codex_multi_agent/deploy/nginx/kite-window-finder-api.conf)
- [env.example](/Users/frederikberger/repositories/codex_multi_agent/deploy/env.example)

Auf dem VPS (Ubuntu/Debian) als `root`:

```bash
apt-get update && apt-get install -y git
git clone https://github.com/<dein-user>/kite_window_finder.git
cd kite_window_finder
DOMAIN=api.deine-domain.tld REPO_URL=https://github.com/<dein-user>/kite_window_finder.git bash deploy/setup_hostinger_vps.sh
```

Danach `.env` pruefen/setzen:

```bash
nano /opt/kite_window_finder/.env
```

TLS aktivieren:

```bash
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d api.deine-domain.tld
```

Optional:
- `METEOSTAT_API_KEY=...`
- `METEOSTAT_API_HOST=meteostat.p.rapidapi.com`

### 2. Frontend-API eintragen

In [frontend/config.js](/Users/frederikberger/repositories/codex_multi_agent/frontend/config.js):

```js
window.APP_CONFIG = {
  API_BASE_URL: "https://api.deine-domain.tld",
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
2. VPS-Setup ausfuehren
3. API-URL in `frontend/config.js` eintragen
4. nochmal nach GitHub pushen
5. GitHub Pages oeffnen
