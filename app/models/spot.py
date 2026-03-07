from typing import Literal

from pydantic import BaseModel, Field


class Sector(BaseModel):
    start_deg: int = Field(ge=0, le=359)
    end_deg: int = Field(ge=0, le=359)


class TideWindows(BaseModel):
    optimal: str
    ok: str
    poor: str


class TidePenaltyRule(BaseModel):
    when: Literal["below", "above"]
    threshold_m: float
    penalty_stars: float = Field(ge=0.5, le=1.5)
    reason: str


class Spot(BaseModel):
    id: str
    country: str
    name: str
    timezone: str
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    shoreline_bearing_deg: int = Field(ge=0, le=359)
    offshore_sector_deg: Sector
    preferred_wind_sector_deg: Sector
    tide_windows: TideWindows
    min_safe_tide_m: float | None = None
    tide_penalties: list[TidePenaltyRule] = Field(default_factory=list)
    depth_profile: str
    spot_notes: str
