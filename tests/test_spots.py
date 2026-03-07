from fastapi.testclient import TestClient

from app.main import app


def test_spots_endpoint_returns_all_configured_spots() -> None:
    client = TestClient(app)

    response = client.get("/spots")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 22
    assert data[0]["id"] == "denmark-hvide-sande"


def test_spots_items_have_minimum_required_fields() -> None:
    client = TestClient(app)

    response = client.get("/spots")
    first = response.json()[0]

    assert "lat" in first
    assert "lon" in first
    assert "shoreline_bearing_deg" in first
    assert "offshore_sector_deg" in first
    assert "preferred_wind_sector_deg" in first
    assert "timezone" in first
    assert "tide_windows" in first
