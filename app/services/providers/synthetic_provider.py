from datetime import UTC, datetime, timedelta
from math import cos, pi, sin

from app.models.spot import Spot
from app.models.weather import ForecastModelName, ForecastPoint, ObservationPoint
from app.services.providers.base import ForecastProvider, ObservationProvider


def _hourly_range(start: datetime, end: datetime) -> list[datetime]:
    if start > end:
        return []
    current = start.replace(minute=0, second=0, microsecond=0, tzinfo=UTC)
    stop = end.replace(minute=0, second=0, microsecond=0, tzinfo=UTC)
    hours: list[datetime] = []
    while current <= stop:
        hours.append(current)
        current += timedelta(hours=1)
    return hours


def _solar_and_daylight(ts: datetime, lat: float, lon: float) -> tuple[float, bool]:
    day = ts.timetuple().tm_yday
    local_hour = (ts.hour + lon / 15) % 24
    day_length = max(8.0, min(16.0, 12.0 + 4.0 * sin(2 * pi * day / 365) * cos(lat * pi / 180)))
    sunrise = 12 - day_length / 2
    sunset = 12 + day_length / 2
    is_daylight = sunrise <= local_hour <= sunset
    if not is_daylight:
        return 0.0, False
    progress = (local_hour - sunrise) / max(0.01, (sunset - sunrise))
    radiation = max(0.0, 900.0 * sin(pi * progress))
    return radiation, True


def _base_wind_speed(ts: datetime, lat: float, lon: float) -> float:
    phase = (lon % 30) / 30 * pi
    diurnal = sin(2 * pi * (ts.hour / 24) + phase)
    seasonal = sin(2 * pi * ts.timetuple().tm_yday / 365)
    raw = 17 + 6 * diurnal + 4 * seasonal - abs(lat) * 0.04
    return max(4.0, min(38.0, raw))


def _base_wind_dir(ts: datetime, lon: float) -> int:
    direction = 220 + 45 * sin(2 * pi * (ts.hour / 24)) + (lon % 25)
    return int(round(direction)) % 360


def _tide_level(ts: datetime, lon: float) -> float:
    hours = ts.timestamp() / 3600
    return 1.2 * sin(2 * pi * (hours / 12.42 + lon / 360))


def _air_temp(ts: datetime, lat: float) -> float:
    diurnal = 5 * sin(2 * pi * ((ts.hour - 5) / 24))
    seasonal = 7 * sin(2 * pi * ts.timetuple().tm_yday / 365)
    return 24 - abs(lat) * 0.18 + diurnal + seasonal


def _water_temp(ts: datetime, lat: float) -> float:
    seasonal = 3.5 * sin(2 * pi * (ts.timetuple().tm_yday - 40) / 365)
    return 24 - abs(lat) * 0.22 + seasonal


class SyntheticForecastProvider(ForecastProvider):
    _MODEL_WIND_BIAS: dict[ForecastModelName, float] = {"ecmwf": 0.6, "gfs": -0.8, "icon": 0.2}
    _MODEL_DIR_BIAS: dict[ForecastModelName, int] = {"ecmwf": 6, "gfs": -10, "icon": 3}

    def hourly_forecast(
        self,
        spot: Spot,
        dt_from: datetime,
        dt_to: datetime,
        model: ForecastModelName,
    ) -> list[ForecastPoint]:
        points: list[ForecastPoint] = []
        for ts in _hourly_range(dt_from, dt_to):
            radiation, is_daylight = _solar_and_daylight(ts, spot.lat, spot.lon)
            speed = _base_wind_speed(ts, spot.lat, spot.lon) + self._MODEL_WIND_BIAS[model]
            direction = (_base_wind_dir(ts, spot.lon) + self._MODEL_DIR_BIAS[model]) % 360
            points.append(
                ForecastPoint(
                    timestamp=ts,
                    model=model,
                    wind_speed_kn=round(max(0.0, speed), 1),
                    wind_direction_deg=direction,
                    tide_level_m=round(_tide_level(ts, spot.lon), 2),
                    air_temp_c=round(_air_temp(ts, spot.lat), 1),
                    water_temp_c=round(_water_temp(ts, spot.lat), 1),
                    shortwave_radiation_wm2=round(radiation, 1),
                    cloud_cover_pct=int(max(0, min(100, 60 - radiation / 25))),
                    precipitation_mm=0.0 if radiation > 120 else 0.2,
                    is_daylight=is_daylight,
                )
            )
        return points


class SyntheticObservationProvider(ObservationProvider):
    def hourly_observations(
        self,
        spot: Spot,
        dt_from: datetime,
        dt_to: datetime,
    ) -> list[ObservationPoint]:
        points: list[ObservationPoint] = []
        spot_bias = (hash(spot.id) % 7 - 3) * 0.3
        for ts in _hourly_range(dt_from, dt_to):
            base_speed = _base_wind_speed(ts, spot.lat, spot.lon)
            noise = 0.8 * sin(ts.timestamp() / 3600 / 9)
            speed = max(0.0, base_speed + spot_bias + noise)
            direction = int(round((_base_wind_dir(ts, spot.lon) + 2 * sin(ts.hour / 3)) % 360))
            points.append(
                ObservationPoint(
                    timestamp=ts,
                    wind_speed_kn=round(speed, 1),
                    wind_direction_deg=direction,
                )
            )
        return points
