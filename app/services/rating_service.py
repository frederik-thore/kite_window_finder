from datetime import UTC, date, datetime, time
from math import floor
from zoneinfo import ZoneInfo

from app.models.adjustment import Adjustment
from app.models.rating import ExplainResponse, RatingDayResponse, RatingExplanation, RatingPoint
from app.models.spot import Sector, Spot
from app.models.timeseries import TimeSeriesResponse
from app.models.weather import ForecastModelName, ForecastPoint
from app.services.adjustments_service import get_adjustment
from app.services.weather_service import hourly_forecast, hourly_observations, model_skill


def _in_sector(direction_deg: int, sector: Sector) -> bool:
    if sector.start_deg <= sector.end_deg:
        return sector.start_deg <= direction_deg <= sector.end_deg
    return direction_deg >= sector.start_deg or direction_deg <= sector.end_deg


def _round_half(value: float) -> float:
    return floor(value * 2 + 0.5) / 2


def _apply_adjustment(point: ForecastPoint, adjustment: Adjustment) -> ForecastPoint:
    wind_direction = (point.wind_direction_deg + adjustment.wind_direction_offset_deg) % 360
    return point.model_copy(
        update={
            "wind_speed_kn": max(0.0, point.wind_speed_kn + adjustment.wind_speed_offset_kn),
            "wind_direction_deg": wind_direction,
        }
    )


def _wind_score(wind_kn: float) -> float:
    if wind_kn < 10:
        return 0.0
    if wind_kn < 12:
        return 0.60
    if wind_kn < 16:
        return 0.85
    if wind_kn <= 24:
        return 1.00
    if wind_kn <= 30:
        return 0.70
    return 0.40


def _direction_score(direction_deg: int, spot: Spot) -> float:
    if _in_sector(direction_deg, spot.offshore_sector_deg):
        return 0.0
    if _in_sector(direction_deg, spot.preferred_wind_sector_deg):
        return 1.0
    return 0.75


def _tide_score(tide_level_m: float, spot: Spot) -> float:
    optimal = spot.tide_windows.optimal
    if optimal == "all":
        return 1.0
    if optimal == "mid":
        if -0.4 <= tide_level_m <= 0.6:
            return 1.0
        return 0.6
    if optimal == "mid-high":
        if 0.0 <= tide_level_m <= 1.0:
            return 1.0
        if -0.4 <= tide_level_m < 0.0:
            return 0.6
        return 0.35
    return 0.7


def _thermal_score(air_c: float, water_c: float, wind_kn: float, radiation: float) -> float:
    if water_c > 24:
        score = 1.0
    elif water_c > 20:
        score = 0.9
    elif water_c > 16:
        score = 0.75
    elif water_c > 12:
        score = 0.55
    else:
        score = 0.35
    if wind_kn >= 18:
        score -= 0.1
    if radiation < 250:
        score -= 0.1
    if air_c < 20:
        score -= 0.1
    return max(0.0, round(score, 3))


def _spot_score(spot: Spot) -> float:
    if spot.depth_profile == "shallow":
        return 0.95
    if spot.depth_profile == "mixed":
        return 0.9
    if spot.depth_profile == "medium":
        return 0.88
    return 0.82


def _neoprene_recommendation(air_c: float, water_c: float, wind_kn: float, radiation: float) -> str:
    levels = ["2/2 or Shorty", "3/2", "4/3", "5/4", "6/5+"]
    if water_c > 25:
        idx = 0
    elif water_c >= 21:
        idx = 1
    elif water_c >= 17:
        idx = 2
    elif water_c >= 13:
        idx = 3
    else:
        idx = 4
    if wind_kn >= 22:
        idx += 1
    if radiation < 180:
        idx += 1
    if air_c < 17:
        idx += 1
    idx = max(0, min(4, idx))
    return levels[idx]


def _gate_reasons(forecast: ForecastPoint, spot: Spot) -> list[str]:
    reasons: list[str] = []
    if _in_sector(forecast.wind_direction_deg, spot.offshore_sector_deg):
        reasons.append("offshore_or_cross_offshore")
    if forecast.wind_speed_kn < 10:
        reasons.append("wind_below_10_kn")
    if not forecast.is_daylight:
        reasons.append("no_daylight")
    return reasons


def _tide_penalty_stars(tide_level_m: float, spot: Spot) -> float:
    penalty = 0.0
    for rule in spot.tide_penalties:
        if rule.when == "below" and tide_level_m < rule.threshold_m:
            penalty = max(penalty, rule.penalty_stars)
        if rule.when == "above" and tide_level_m > rule.threshold_m:
            penalty = max(penalty, rule.penalty_stars)
    if penalty == 0.0 and spot.min_safe_tide_m is not None and tide_level_m < spot.min_safe_tide_m:
        penalty = 1.0
    return penalty


def build_rating_point(
    spot: Spot,
    forecast: ForecastPoint,
    observation_wind_speed: float | None,
    observation_wind_direction: int | None,
) -> RatingPoint:
    low_tide_penalty_stars = _tide_penalty_stars(forecast.tide_level_m, spot)
    gates = _gate_reasons(forecast, spot)
    if gates:
        explanation = RatingExplanation(
            hard_gates_triggered=gates,
            components={
                "S_wind": 0,
                "S_dir": 0,
                "S_tide": 0,
                "S_thermal": 0,
                "S_spot": 0,
                "tide_penalty_stars": low_tide_penalty_stars,
            },
            weighted_score=0,
        )
        stars = 0.0
    else:
        s_wind = _wind_score(forecast.wind_speed_kn)
        s_dir = _direction_score(forecast.wind_direction_deg, spot)
        s_tide = _tide_score(forecast.tide_level_m, spot)
        s_thermal = _thermal_score(
            forecast.air_temp_c,
            forecast.water_temp_c,
            forecast.wind_speed_kn,
            forecast.shortwave_radiation_wm2,
        )
        s_spot = _spot_score(spot)
        weighted = 0.30 * s_wind + 0.25 * s_dir + 0.20 * s_tide + 0.20 * s_thermal + 0.05 * s_spot
        stars = max(0.0, _round_half(5 * weighted) - low_tide_penalty_stars)
        explanation = RatingExplanation(
            hard_gates_triggered=[],
            components={
                "S_wind": round(s_wind, 3),
                "S_dir": round(s_dir, 3),
                "S_tide": round(s_tide, 3),
                "S_thermal": round(s_thermal, 3),
                "S_spot": round(s_spot, 3),
                "tide_penalty_stars": low_tide_penalty_stars,
            },
            weighted_score=round(weighted, 3),
        )
    return RatingPoint(
        timestamp=forecast.timestamp,
        stars=stars,
        forecast=forecast,
        observation=(
            {
                "timestamp": forecast.timestamp,
                "wind_speed_kn": observation_wind_speed,
                "wind_direction_deg": observation_wind_direction,
            }
            if observation_wind_speed is not None and observation_wind_direction is not None
            else None
        ),
        neoprene_recommendation=_neoprene_recommendation(
            forecast.air_temp_c,
            forecast.water_temp_c,
            forecast.wind_speed_kn,
            forecast.shortwave_radiation_wm2,
        ),
        explanation=explanation,
    )


def rating_for_day(
    spot: Spot, requested_date: date, model: ForecastModelName | None = None
) -> RatingDayResponse:
    spot_tz = ZoneInfo(spot.timezone)
    local_start = datetime.combine(requested_date, time.min, tzinfo=spot_tz)
    local_end = datetime.combine(requested_date, time.max, tzinfo=spot_tz)
    start = local_start.astimezone(UTC)
    end = local_end.astimezone(UTC)
    adjustment = get_adjustment(spot.id)
    selected_model = model or model_skill(spot).active_model
    forecast_raw = hourly_forecast(spot, start, end, selected_model)
    forecast = [_apply_adjustment(point, adjustment) for point in forecast_raw]
    observations = {}
    now = datetime.now(tz=UTC)
    if start <= now:
        observation_end = min(end, now)
        observation_rows = hourly_observations(spot, start, observation_end)
        observations = {row.timestamp: row for row in observation_rows}
    points: list[RatingPoint] = []
    for point in forecast:
        observation = observations.get(point.timestamp)
        points.append(
            build_rating_point(
                spot,
                point,
                observation_wind_speed=observation.wind_speed_kn if observation else None,
                observation_wind_direction=observation.wind_direction_deg if observation else None,
            )
        )
    return RatingDayResponse(spot_id=spot.id, date=requested_date.isoformat(), points=points)


def explain_at(
    spot: Spot, timestamp: datetime, model: ForecastModelName | None = None
) -> ExplainResponse:
    day = rating_for_day(spot, timestamp.date(), model=model)
    for point in day.points:
        if point.timestamp == timestamp:
            return ExplainResponse(spot_id=spot.id, point=point)
    raise ValueError("Timestamp not available for requested day.")


def timeseries_for_range(
    spot: Spot,
    dt_from: datetime,
    dt_to: datetime,
    model: ForecastModelName | None = None,
) -> TimeSeriesResponse:
    if dt_from.tzinfo is None:
        dt_from = dt_from.replace(tzinfo=UTC)
    if dt_to.tzinfo is None:
        dt_to = dt_to.replace(tzinfo=UTC)
    if dt_from > dt_to:
        dt_from, dt_to = dt_to, dt_from
    adjustment = get_adjustment(spot.id)
    selected_model = model or model_skill(spot).active_model
    forecast_raw = hourly_forecast(spot, dt_from, dt_to, selected_model)
    forecast = [_apply_adjustment(point, adjustment) for point in forecast_raw]
    observations = {}
    now = datetime.now(tz=UTC)
    if dt_from <= now:
        observation_end = min(dt_to, now)
        observations = {
            row.timestamp: row for row in hourly_observations(spot, dt_from, observation_end)
        }
    points: list[RatingPoint] = []
    for point in forecast:
        observation = observations.get(point.timestamp)
        points.append(
            build_rating_point(
                spot,
                point,
                observation_wind_speed=observation.wind_speed_kn if observation else None,
                observation_wind_direction=observation.wind_direction_deg if observation else None,
            )
        )
    return TimeSeriesResponse(
        spot_id=spot.id,
        from_iso=dt_from.isoformat(),
        to_iso=dt_to.isoformat(),
        points=points,
    )
