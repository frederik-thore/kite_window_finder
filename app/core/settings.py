"""Central application settings."""

import os

API_TITLE = "Kite Window Finder API"
API_VERSION = "0.1.0"


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


LIVE_WEATHER_ENABLED = _bool_env("LIVE_WEATHER_ENABLED", True)
ALLOW_SYNTHETIC_FALLBACK = _bool_env("ALLOW_SYNTHETIC_FALLBACK", False)
PROVIDER_HTTP_TIMEOUT_SECONDS = float(os.getenv("PROVIDER_HTTP_TIMEOUT_SECONDS", "6"))
PROVIDER_CACHE_TTL_SECONDS = int(os.getenv("PROVIDER_CACHE_TTL_SECONDS", "900"))
FORECAST_PROVIDER_CACHE_TTL_SECONDS = int(
    os.getenv("FORECAST_PROVIDER_CACHE_TTL_SECONDS", str(PROVIDER_CACHE_TTL_SECONDS))
)
OBSERVATION_PROVIDER_CACHE_TTL_SECONDS = int(
    os.getenv("OBSERVATION_PROVIDER_CACHE_TTL_SECONDS", str(PROVIDER_CACHE_TTL_SECONDS))
)
METEOSTAT_API_KEY = os.getenv("METEOSTAT_API_KEY")
METEOSTAT_API_HOST = os.getenv("METEOSTAT_API_HOST", "meteostat.p.rapidapi.com")
CORS_ALLOW_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")
    if origin.strip()
]
