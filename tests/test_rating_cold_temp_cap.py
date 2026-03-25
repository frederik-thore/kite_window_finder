from datetime import UTC, datetime

import pytest

from app.models.weather import ForecastPoint
from app.services.rating_service import build_rating_point
from app.services.spots_service import get_spot


@pytest.mark.parametrize(
    ("air_c", "water_c"),
    [
        (9.0, 18.0),
        (18.0, 9.0),
    ],
)
def test_cold_air_or_water_caps_stars_to_three(air_c: float, water_c: float) -> None:
    spot = get_spot("egypt-el-gouna")
    assert spot is not None
    forecast = ForecastPoint(
        timestamp=datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
        model="gfs",
        wind_speed_kn=20.0,
        wind_direction_deg=300,
        tide_level_m=0.3,
        air_temp_c=air_c,
        water_temp_c=water_c,
        shortwave_radiation_wm2=700.0,
        cloud_cover_pct=5,
        precipitation_mm=0.0,
        is_daylight=True,
    )
    point = build_rating_point(
        spot=spot,
        forecast=forecast,
        observation_wind_speed=None,
        observation_wind_direction=None,
    )
    assert point.stars <= 3.0
