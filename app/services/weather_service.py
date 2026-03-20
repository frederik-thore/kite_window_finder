from datetime import UTC, datetime, timedelta
from math import fabs

from app.core.settings import (
    ALLOW_SYNTHETIC_FALLBACK,
    LIVE_WEATHER_ENABLED,
    METEOSTAT_API_HOST,
    METEOSTAT_API_KEY,
)
from app.models.skill import ModelSkillEntry, ModelSkillResponse
from app.models.spot import Spot
from app.models.weather import ForecastModelName, ForecastPoint, ObservationPoint
from app.services.providers.open_meteo_provider import (
    MeteostatObservationProvider,
    OpenMeteoArchiveObservationProvider,
    OpenMeteoForecastProvider,
)
from app.services.providers.synthetic_provider import (
    SyntheticForecastProvider,
    SyntheticObservationProvider,
)

MODELS: list[ForecastModelName] = ["ecmwf", "gfs", "icon"]

_fallback_forecast = SyntheticForecastProvider()
_fallback_observation = SyntheticObservationProvider()

_live_forecast = OpenMeteoForecastProvider()
_live_observation_archive = OpenMeteoArchiveObservationProvider()
_live_observation_meteostat = (
    MeteostatObservationProvider(METEOSTAT_API_KEY, METEOSTAT_API_HOST)
    if METEOSTAT_API_KEY
    else None
)
_MODEL_SKILL_CACHE: dict[tuple[str, int], tuple[datetime, ModelSkillResponse]] = {}


def _angle_error(a: int, b: int) -> float:
    diff = fabs(a - b) % 360
    return min(diff, 360 - diff)


def hourly_observations(spot: Spot, dt_from: datetime, dt_to: datetime) -> list[ObservationPoint]:
    if LIVE_WEATHER_ENABLED:
        if _live_observation_meteostat:
            try:
                points = list(_live_observation_meteostat.hourly_observations(spot, dt_from, dt_to))
                if points:
                    return points
            except Exception:
                pass
        try:
            points = list(_live_observation_archive.hourly_observations(spot, dt_from, dt_to))
            if points:
                return points
        except Exception:
            pass
    if ALLOW_SYNTHETIC_FALLBACK:
        return list(_fallback_observation.hourly_observations(spot, dt_from, dt_to))
    raise RuntimeError("Live observation data unavailable and synthetic fallback is disabled.")


def hourly_forecast(
    spot: Spot, dt_from: datetime, dt_to: datetime, model: ForecastModelName
) -> list[ForecastPoint]:
    if LIVE_WEATHER_ENABLED:
        try:
            points = list(_live_forecast.hourly_forecast(spot, dt_from, dt_to, model))
            if points:
                return points
        except Exception:
            pass
    if ALLOW_SYNTHETIC_FALLBACK:
        return list(_fallback_forecast.hourly_forecast(spot, dt_from, dt_to, model))
    raise RuntimeError("Live forecast data unavailable and synthetic fallback is disabled.")


def model_skill(spot: Spot, window_days: int = 30) -> ModelSkillResponse:
    cache_key = (spot.id, window_days)
    now = datetime.now(tz=UTC)
    cached = _MODEL_SKILL_CACHE.get(cache_key)
    if cached and (now - cached[0]).total_seconds() < 1800:
        return cached[1]

    end = now.replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=window_days)
    observations_unavailable = False
    try:
        obs = hourly_observations(spot, start, end)
    except RuntimeError:
        obs = []
        observations_unavailable = True
    by_time = {item.timestamp: item for item in obs}
    if not by_time:
        observations_unavailable = True

    entries: list[ModelSkillEntry] = []
    for model in MODELS:
        try:
            forecast = hourly_forecast(spot, start, end, model)
        except RuntimeError:
            continue
        if observations_unavailable:
            entries.append(
                ModelSkillEntry(
                    model=model,
                    mae_wind_kn=0.0,
                    mae_dir_deg=0.0,
                    kiteable_hit_rate=0.0,
                    model_skill=0.5,
                )
            )
            continue
        pairs = [(point, by_time.get(point.timestamp)) for point in forecast]
        valid_pairs = [(point, observed) for point, observed in pairs if observed is not None]
        count = len(valid_pairs)
        if count == 0:
            continue
        wind_errors = 0.0
        dir_errors = 0.0
        kite_hits = 0
        for point, observed in valid_pairs:
            wind_errors += abs(point.wind_speed_kn - observed.wind_speed_kn)
            dir_errors += _angle_error(point.wind_direction_deg, observed.wind_direction_deg)
            pred_kiteable = point.wind_speed_kn >= 10 and point.is_daylight
            obs_kiteable = observed.wind_speed_kn >= 10
            kite_hits += int(pred_kiteable == obs_kiteable)
        mae_wind = wind_errors / count
        mae_dir = dir_errors / count
        hit_rate = kite_hits / count
        wind_norm = min(mae_wind / 12.0, 1.0)
        dir_norm = min(mae_dir / 90.0, 1.0)
        skill = 0.50 * (1 - wind_norm) + 0.30 * (1 - dir_norm) + 0.20 * hit_rate
        entries.append(
            ModelSkillEntry(
                model=model,
                mae_wind_kn=round(mae_wind, 2),
                mae_dir_deg=round(mae_dir, 2),
                kiteable_hit_rate=round(hit_rate, 3),
                model_skill=round(skill, 3),
            )
        )
    entries.sort(key=lambda item: item.model_skill, reverse=True)
    if not entries:
        raise RuntimeError("No live forecast models available for model correlation.")
    if observations_unavailable and any(item.model == "gfs" for item in entries):
        active = "gfs"
    else:
        active = entries[0].model if entries else "ecmwf"
    response = ModelSkillResponse(
        spot_id=spot.id,
        window_days=window_days,
        active_model=active,
        entries=entries,
    )
    _MODEL_SKILL_CACHE[cache_key] = (now, response)
    return response
