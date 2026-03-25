from datetime import UTC, datetime

import pytest

from app.models.weather import ForecastPoint
from app.services.rating_service import build_rating_point
from app.services.spots_service import get_spot


@pytest.mark.parametrize(
    ("wind_kn", "expected_stars"),
    [
        (12.0, 4.0),
        (14.0, 4.5),
        (15.0, 5.0),
    ],
)
def test_wind_band_caps_for_maximum_stars(wind_kn: float, expected_stars: float) -> None:
    spot = get_spot("egypt-seahorse-bay")
    assert spot is not None
    forecast = ForecastPoint(
        timestamp=datetime(2026, 3, 25, 12, 0, tzinfo=UTC),
        model="gfs",
        wind_speed_kn=wind_kn,
        wind_direction_deg=300,
        tide_level_m=0.3,
        air_temp_c=30.0,
        water_temp_c=26.0,
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

    assert point.stars == expected_stars
