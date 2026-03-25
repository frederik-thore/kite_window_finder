from datetime import UTC, datetime
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import httpx

from app.core.settings import (
    FORECAST_PROVIDER_CACHE_TTL_SECONDS,
    OBSERVATION_PROVIDER_CACHE_TTL_SECONDS,
    PROVIDER_CACHE_TTL_SECONDS,
    PROVIDER_HTTP_TIMEOUT_SECONDS,
)
from app.models.spot import Spot
from app.models.weather import ForecastModelName, ForecastPoint, ObservationPoint
from app.services.providers.base import ForecastProvider, ObservationProvider
from app.services.providers.cache import TTLCache

KNOTS_PER_KMH = 0.539957

_FORECAST_BASE_BY_MODEL: dict[ForecastModelName, str] = {
    "ecmwf": "https://api.open-meteo.com/v1/ecmwf",
    "gfs": "https://api.open-meteo.com/v1/gfs",
    "icon": "https://api.open-meteo.com/v1/dwd-icon",
}


def _iso(ts: datetime) -> str:
    return ts.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _date_window_key(dt_from: datetime, dt_to: datetime) -> str:
    return f"{dt_from.date().isoformat()}:{dt_to.date().isoformat()}"


def _parse_time(values: list[str], timezone_name: str) -> list[datetime]:
    timezone = ZoneInfo(timezone_name)
    parsed: list[datetime] = []
    for item in values:
        ts = datetime.fromisoformat(item.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone)
        parsed.append(ts.astimezone(UTC))
    return parsed


def _filter_between(ts: datetime, dt_from: datetime, dt_to: datetime) -> bool:
    return dt_from <= ts <= dt_to


class OpenMeteoForecastProvider(ForecastProvider):
    def __init__(self) -> None:
        ttl_seconds = FORECAST_PROVIDER_CACHE_TTL_SECONDS or PROVIDER_CACHE_TTL_SECONDS
        self._cache: TTLCache[list[ForecastPoint]] = TTLCache(ttl_seconds)

    def hourly_forecast(
        self,
        spot: Spot,
        dt_from: datetime,
        dt_to: datetime,
        model: ForecastModelName,
    ) -> list[ForecastPoint]:
        dt_from = dt_from.astimezone(UTC)
        dt_to = dt_to.astimezone(UTC)
        cache_key = f"forecast:{spot.id}:{model}:{_date_window_key(dt_from, dt_to)}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        weather_data = self._fetch_weather(spot, dt_from, dt_to, model)
        marine_data = self._fetch_marine(spot, dt_from, dt_to)
        points = self._merge_forecast(spot, model, weather_data, marine_data, dt_from, dt_to)
        self._cache.set(cache_key, points)
        return points

    def _fetch_weather(
        self, spot: Spot, dt_from: datetime, dt_to: datetime, model: ForecastModelName
    ) -> dict:
        params = {
            "latitude": spot.lat,
            "longitude": spot.lon,
            "timezone": spot.timezone,
            "wind_speed_unit": "kn",
            "start_date": dt_from.date().isoformat(),
            "end_date": dt_to.date().isoformat(),
            "hourly": ",".join(
                [
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "temperature_2m",
                    "shortwave_radiation",
                    "cloud_cover",
                    "precipitation",
                ]
            ),
            "daily": "sunrise,sunset",
        }
        url = _FORECAST_BASE_BY_MODEL[model]
        with httpx.Client(timeout=PROVIDER_HTTP_TIMEOUT_SECONDS) as client:
            response = client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def _fetch_marine(self, spot: Spot, dt_from: datetime, dt_to: datetime) -> dict:
        params = {
            "latitude": spot.lat,
            "longitude": spot.lon,
            "timezone": spot.timezone,
            "start_date": dt_from.date().isoformat(),
            "end_date": dt_to.date().isoformat(),
            "hourly": "sea_level_height_msl,sea_surface_temperature",
        }
        with httpx.Client(timeout=PROVIDER_HTTP_TIMEOUT_SECONDS) as client:
            response = client.get("https://marine-api.open-meteo.com/v1/marine", params=params)
        response.raise_for_status()
        return response.json()

    def _merge_forecast(
        self,
        spot: Spot,
        model: ForecastModelName,
        weather_data: dict,
        marine_data: dict,
        dt_from: datetime,
        dt_to: datetime,
    ) -> list[ForecastPoint]:
        weather_hourly = weather_data["hourly"]
        marine_hourly = marine_data["hourly"]
        source_timezone = weather_data.get("timezone", spot.timezone)
        marine_timezone = marine_data.get("timezone", source_timezone)

        marine_by_time: dict[datetime, tuple[float, float]] = {}
        marine_times = _parse_time(marine_hourly["time"], marine_timezone)
        for idx, ts in enumerate(marine_times):
            marine_by_time[ts] = (
                float(marine_hourly.get("sea_level_height_msl", [0])[idx]),
                float(marine_hourly.get("sea_surface_temperature", [0])[idx]),
            )

        daylight_by_day: dict[str, tuple[datetime, datetime]] = {}
        daily = weather_data.get("daily", {})
        if daily.get("time") and daily.get("sunrise") and daily.get("sunset"):
            sunrise_times = _parse_time(daily["sunrise"], source_timezone)
            sunset_times = _parse_time(daily["sunset"], source_timezone)
            for idx, day_key in enumerate(daily["time"]):
                daylight_by_day[day_key] = (sunrise_times[idx], sunset_times[idx])

        points: list[ForecastPoint] = []
        times = _parse_time(weather_hourly["time"], source_timezone)
        for idx, ts in enumerate(times):
            if not _filter_between(ts, dt_from, dt_to):
                continue
            tide_m, water_temp = marine_by_time.get(ts, (0.0, 20.0))
            radiation = float(weather_hourly.get("shortwave_radiation", [0])[idx] or 0.0)
            local_day_key = ts.astimezone(ZoneInfo(source_timezone)).date().isoformat()
            sunrise_sunset = daylight_by_day.get(local_day_key)
            is_day = radiation > 0
            if sunrise_sunset is not None:
                sunrise, sunset = sunrise_sunset
                is_day = sunrise <= ts < sunset
            points.append(
                ForecastPoint(
                    timestamp=ts,
                    model=model,
                    wind_speed_kn=float(weather_hourly["wind_speed_10m"][idx]),
                    wind_direction_deg=int(round(weather_hourly["wind_direction_10m"][idx])) % 360,
                    tide_level_m=round(tide_m, 2),
                    air_temp_c=float(weather_hourly["temperature_2m"][idx]),
                    water_temp_c=round(water_temp, 1),
                    shortwave_radiation_wm2=round(radiation, 1),
                    cloud_cover_pct=int(round(weather_hourly.get("cloud_cover", [0])[idx] or 0)),
                    precipitation_mm=float(weather_hourly.get("precipitation", [0])[idx] or 0.0),
                    is_daylight=is_day,
                )
            )
        return points


class OpenMeteoArchiveObservationProvider(ObservationProvider):
    def __init__(self) -> None:
        ttl_seconds = OBSERVATION_PROVIDER_CACHE_TTL_SECONDS or PROVIDER_CACHE_TTL_SECONDS
        self._cache: TTLCache[list[ObservationPoint]] = TTLCache(ttl_seconds)

    def hourly_observations(
        self,
        spot: Spot,
        dt_from: datetime,
        dt_to: datetime,
    ) -> list[ObservationPoint]:
        dt_from = dt_from.astimezone(UTC)
        dt_to = dt_to.astimezone(UTC)
        cache_key = f"obs_archive:{spot.id}:{_date_window_key(dt_from, dt_to)}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        params = {
            "latitude": spot.lat,
            "longitude": spot.lon,
            "timezone": "UTC",
            "wind_speed_unit": "kn",
            "start_date": dt_from.date().isoformat(),
            "end_date": dt_to.date().isoformat(),
            "hourly": "wind_speed_10m,wind_direction_10m",
        }
        with httpx.Client(timeout=PROVIDER_HTTP_TIMEOUT_SECONDS) as client:
            response = client.get("https://archive-api.open-meteo.com/v1/archive", params=params)
        response.raise_for_status()
        data = response.json()["hourly"]
        points: list[ObservationPoint] = []
        for idx, raw_time in enumerate(data["time"]):
            ts = datetime.fromisoformat(raw_time).replace(tzinfo=UTC)
            if not _filter_between(ts, dt_from, dt_to):
                continue
            points.append(
                ObservationPoint(
                    timestamp=ts,
                    wind_speed_kn=float(data["wind_speed_10m"][idx]),
                    wind_direction_deg=int(round(data["wind_direction_10m"][idx])) % 360,
                )
            )
        self._cache.set(cache_key, points)
        return points


class MeteostatObservationProvider(ObservationProvider):
    def __init__(self, api_key: str, api_host: str) -> None:
        self._api_key = api_key
        self._api_host = api_host
        ttl_seconds = OBSERVATION_PROVIDER_CACHE_TTL_SECONDS or PROVIDER_CACHE_TTL_SECONDS
        self._cache: TTLCache[list[ObservationPoint]] = TTLCache(ttl_seconds)

    def hourly_observations(
        self,
        spot: Spot,
        dt_from: datetime,
        dt_to: datetime,
    ) -> list[ObservationPoint]:
        dt_from = dt_from.astimezone(UTC)
        dt_to = dt_to.astimezone(UTC)
        cache_key = f"obs_meteostat:{spot.id}:{_date_window_key(dt_from, dt_to)}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        headers = {
            "X-RapidAPI-Key": self._api_key,
            "X-RapidAPI-Host": self._api_host,
        }
        nearby_params = {"lat": spot.lat, "lon": spot.lon, "limit": 1}
        base_url = f"https://{self._api_host}"
        with httpx.Client(timeout=PROVIDER_HTTP_TIMEOUT_SECONDS, headers=headers) as client:
            nearby = client.get(f"{base_url}/stations/nearby", params=nearby_params)
            nearby.raise_for_status()
            nearby_data = nearby.json().get("data", [])
            if not nearby_data:
                raise RuntimeError("No nearby Meteostat station found.")
            station_id = nearby_data[0]["id"]
            hourly_params = {
                "station": station_id,
                "start": dt_from.date().isoformat(),
                "end": dt_to.date().isoformat(),
                "tz": "UTC",
            }
            hourly = client.get(f"{base_url}/stations/hourly", params=hourly_params)
            hourly.raise_for_status()
        rows = hourly.json().get("data", [])
        points: list[ObservationPoint] = []
        for row in rows:
            ts = datetime.fromisoformat(row["time"]).replace(tzinfo=UTC)
            if not _filter_between(ts, dt_from, dt_to):
                continue
            wind_kph = float(row.get("wspd") or 0.0)
            points.append(
                ObservationPoint(
                    timestamp=ts,
                    wind_speed_kn=round(wind_kph * KNOTS_PER_KMH, 2),
                    wind_direction_deg=int(round(float(row.get("wdir") or 0.0))) % 360,
                )
            )
        self._cache.set(cache_key, points)
        return points


def cache_key_from_params(prefix: str, params: dict) -> str:
    return f"{prefix}:{urlencode(sorted(params.items()), doseq=True)}"
