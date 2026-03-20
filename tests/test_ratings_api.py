from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app


def test_rating_endpoint_returns_24_hour_points() -> None:
    client = TestClient(app)
    day = (datetime.now(tz=UTC) - timedelta(days=1)).date().isoformat()
    response = client.get("/spots/egypt-el-gouna/rating", params={"day": day})

    assert response.status_code == 200
    payload = response.json()
    assert payload["spot_id"] == "egypt-el-gouna"
    assert len(payload["points"]) == 24


def test_timeseries_endpoint_returns_default_window() -> None:
    client = TestClient(app)
    response = client.get("/spots/egypt-el-gouna/timeseries")

    assert response.status_code == 200
    payload = response.json()
    assert payload["spot_id"] == "egypt-el-gouna"
    assert len(payload["points"]) > 100


def test_model_skill_endpoint_returns_active_model() -> None:
    client = TestClient(app)
    response = client.get("/spots/egypt-el-gouna/model-skill", params={"window": "30d"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["active_model"] in {"ecmwf", "gfs", "icon"}
    assert len(payload["entries"]) == 3


def test_rating_endpoint_can_force_specific_model() -> None:
    client = TestClient(app)
    day = (datetime.now(tz=UTC) - timedelta(days=1)).date().isoformat()
    response = client.get(
        "/spots/egypt-el-gouna/rating",
        params={"day": day, "model": "gfs"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["points"][0]["forecast"]["model"] == "gfs"


def test_future_rating_works_without_observations() -> None:
    client = TestClient(app)
    day = (datetime.now(tz=UTC) + timedelta(days=1)).date().isoformat()
    response = client.get(
        "/spots/egypt-seahorse-bay/rating",
        params={"day": day, "model": "gfs"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["points"]) > 0
    assert any(point["observation"] is None for point in payload["points"])


def test_adjustments_roundtrip() -> None:
    client = TestClient(app)
    write = client.post(
        "/spots/egypt-el-gouna/adjustments",
        json={"wind_speed_offset_kn": 2.5, "wind_direction_offset_deg": 15},
    )
    assert write.status_code == 200
    read = client.get("/spots/egypt-el-gouna/adjustments")
    assert read.status_code == 200
    assert read.json()["adjustment"] == {
        "wind_speed_offset_kn": 2.5,
        "wind_direction_offset_deg": 15,
    }


def test_explain_endpoint_for_known_hour() -> None:
    client = TestClient(app)
    ts = (datetime.now(tz=UTC) - timedelta(days=1)).replace(
        hour=12, minute=0, second=0, microsecond=0
    ).isoformat()
    response = client.get("/spots/egypt-el-gouna/explain", params={"timestamp": ts})

    assert response.status_code == 200
    payload = response.json()
    assert payload["spot_id"] == "egypt-el-gouna"
    assert "point" in payload


def test_rating_rejects_future_beyond_three_days() -> None:
    client = TestClient(app)
    response = client.get("/spots/egypt-el-gouna/rating", params={"day": "2099-01-01"})
    assert response.status_code == 422


def test_rating_rejects_past_beyond_seven_days() -> None:
    client = TestClient(app)
    response = client.get("/spots/egypt-el-gouna/rating", params={"day": "2000-01-01"})
    assert response.status_code == 422


def test_tide_penalties_apply_for_documented_tide_sensitive_spots() -> None:
    client = TestClient(app)
    day = (datetime.now(tz=UTC) - timedelta(days=1)).date().isoformat()
    for spot_id in ["egypt-seahorse-bay", "morocco-dakhla", "zanzibar-jambiani"]:
        response = client.get(f"/spots/{spot_id}/rating", params={"day": day})
        assert response.status_code == 200
        points = response.json()["points"]
        assert any(p["explanation"]["components"].get("tide_penalty_stars", 0) > 0 for p in points)
