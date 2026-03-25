from datetime import UTC, datetime

import app.services.providers.open_meteo_provider as provider_mod
from app.models.spot import Spot, TidePenaltyRule, TideWindows
from app.services.providers.open_meteo_provider import OpenMeteoForecastProvider


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._payload


class _FakeClient:
    weather_calls = 0
    marine_calls = 0

    def __init__(self, *args, **kwargs) -> None:
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def get(self, url: str, params: dict | None = None):
        if "marine-api.open-meteo.com" in url:
            _FakeClient.marine_calls += 1
            return _FakeResponse(
                {
                    "timezone": "Africa/Cairo",
                    "hourly": {
                        "time": ["2026-03-25T12:00"],
                        "sea_level_height_msl": [0.12],
                        "sea_surface_temperature": [21.0],
                    },
                }
            )
        _FakeClient.weather_calls += 1
        return _FakeResponse(
            {
                "timezone": "Africa/Cairo",
                "hourly": {
                    "time": ["2026-03-25T12:00"],
                    "wind_speed_10m": [18.0],
                    "wind_direction_10m": [300],
                    "temperature_2m": [25.0],
                    "shortwave_radiation": [700.0],
                    "cloud_cover": [15],
                    "precipitation": [0.0],
                },
                "daily": {
                    "time": ["2026-03-25"],
                    "sunrise": ["2026-03-25T05:50"],
                    "sunset": ["2026-03-25T17:55"],
                },
            }
        )


def _spot() -> Spot:
    return Spot(
        id="test-spot",
        country="Egypt",
        name="Test Spot",
        lat=27.251,
        lon=33.835,
        timezone="Africa/Cairo",
        shoreline_bearing_deg=0,
        preferred_wind_sector_deg={"start_deg": 250, "end_deg": 340},
        offshore_sector_deg={"start_deg": 20, "end_deg": 120},
        tide_windows=TideWindows(optimal="mid", ok="all", poor="none"),
        min_safe_tide_m=0.0,
        depth_profile="shallow",
        tide_penalties=[
            TidePenaltyRule(
                when="below",
                threshold_m=-0.3,
                penalty_stars=1.0,
                reason="Too shallow at low tide",
            )
        ],
        spot_notes="Test spot for provider cache behavior.",
    )


def test_forecast_provider_reuses_cached_day_window(monkeypatch) -> None:
    monkeypatch.setattr(provider_mod.httpx, "Client", _FakeClient)
    _FakeClient.weather_calls = 0
    _FakeClient.marine_calls = 0
    provider = OpenMeteoForecastProvider()
    spot = _spot()
    dt_from = datetime(2026, 3, 25, 0, 0, tzinfo=UTC)
    dt_to = datetime(2026, 3, 25, 23, 59, tzinfo=UTC)

    first = provider.hourly_forecast(spot, dt_from, dt_to, "gfs")
    second = provider.hourly_forecast(spot, dt_from, dt_to, "gfs")

    assert len(first) == 1
    assert len(second) == 1
    assert _FakeClient.weather_calls == 1
    assert _FakeClient.marine_calls == 1
