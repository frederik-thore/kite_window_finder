from datetime import UTC, date, datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Query

from app.models.adjustment import Adjustment, AdjustmentResponse
from app.models.rating import ExplainResponse, RatingDayResponse
from app.models.skill import ModelSkillResponse
from app.models.timeseries import TimeSeriesResponse
from app.models.weather import ForecastModelName
from app.services.adjustments_service import get_adjustment, set_adjustment
from app.services.rating_service import explain_at, rating_for_day, timeseries_for_range
from app.services.spots_service import get_spot
from app.services.weather_service import model_skill

router = APIRouter(prefix="/spots/{spot_id}", tags=["ratings"])
DayQuery = Annotated[date | None, Query()]
FromQuery = Annotated[datetime | None, Query(alias="from")]
ToQuery = Annotated[datetime | None, Query(alias="to")]
ModelQuery = Annotated[ForecastModelName | None, Query()]

MIN_HISTORY_DAYS = 7
MAX_FORECAST_DAYS = 3


def _must_spot(spot_id: str):
    spot = get_spot(spot_id)
    if not spot:
        raise HTTPException(status_code=404, detail=f"Unknown spot id: {spot_id}")
    return spot


def _validate_day_window(target_day: date, spot_timezone: str) -> None:
    today = datetime.now(tz=ZoneInfo(spot_timezone)).date()
    if target_day < today - timedelta(days=MIN_HISTORY_DAYS):
        raise HTTPException(
            status_code=422,
            detail=f"day is too old; minimum supported is {MIN_HISTORY_DAYS} days in the past",
        )
    if target_day > today + timedelta(days=MAX_FORECAST_DAYS):
        raise HTTPException(
            status_code=422,
            detail=f"day is too far in the future; maximum supported is {MAX_FORECAST_DAYS} days",
        )


def _validate_range_window(dt_from: datetime, dt_to: datetime) -> None:
    today = datetime.now(tz=UTC).date()
    min_day = today - timedelta(days=MIN_HISTORY_DAYS)
    max_day = today + timedelta(days=MAX_FORECAST_DAYS)
    if dt_from.date() < min_day or dt_to.date() > max_day:
        raise HTTPException(
            status_code=422,
            detail=(
                f"supported range is from {min_day.isoformat()} to {max_day.isoformat()} (UTC date)"
            ),
        )


def _handle_data_errors(fn):
    try:
        return fn()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/rating", response_model=RatingDayResponse)
def read_rating_for_day(
    spot_id: str,
    day: DayQuery = None,
    model: ModelQuery = None,
) -> RatingDayResponse:
    spot = _must_spot(spot_id)
    target_day = day or datetime.now(tz=ZoneInfo(spot.timezone)).date()
    _validate_day_window(target_day, spot.timezone)
    return _handle_data_errors(lambda: rating_for_day(spot, target_day, model=model))


@router.get("/timeseries", response_model=TimeSeriesResponse)
def read_timeseries(
    spot_id: str,
    from_iso: FromQuery = None,
    to_iso: ToQuery = None,
    model: ModelQuery = None,
) -> TimeSeriesResponse:
    spot = _must_spot(spot_id)
    if from_iso is None or to_iso is None:
        now = datetime.now(tz=UTC).replace(minute=0, second=0, microsecond=0)
        from_iso = now - timedelta(days=MIN_HISTORY_DAYS)
        to_iso = now + timedelta(days=3)
    _validate_range_window(from_iso, to_iso)
    return _handle_data_errors(lambda: timeseries_for_range(spot, from_iso, to_iso, model=model))


@router.get("/explain", response_model=ExplainResponse)
def read_explain(
    spot_id: str,
    timestamp: datetime,
    model: ModelQuery = None,
) -> ExplainResponse:
    spot = _must_spot(spot_id)
    _validate_day_window(timestamp.date(), spot.timezone)
    return _handle_data_errors(
        lambda: explain_at(
            spot,
            timestamp if timestamp.tzinfo else timestamp.replace(tzinfo=UTC),
            model=model,
        )
    )


@router.get("/model-skill", response_model=ModelSkillResponse)
def read_model_skill(spot_id: str, window: str = Query(default="30d")) -> ModelSkillResponse:
    spot = _must_spot(spot_id)
    parsed = window.lower().strip()
    if not parsed.endswith("d"):
        raise HTTPException(status_code=422, detail="window must follow format '<days>d', e.g. 30d")
    days = int(parsed[:-1])
    if days < 7 or days > 180:
        raise HTTPException(status_code=422, detail="window days must be between 7 and 180")
    return _handle_data_errors(lambda: model_skill(spot, window_days=days))


@router.get("/adjustments", response_model=AdjustmentResponse)
def read_adjustment(spot_id: str) -> AdjustmentResponse:
    _must_spot(spot_id)
    return AdjustmentResponse(spot_id=spot_id, adjustment=get_adjustment(spot_id))


@router.post("/adjustments", response_model=AdjustmentResponse)
def write_adjustment(spot_id: str, adjustment: Adjustment) -> AdjustmentResponse:
    _must_spot(spot_id)
    saved = set_adjustment(spot_id, adjustment)
    return AdjustmentResponse(spot_id=spot_id, adjustment=saved)
