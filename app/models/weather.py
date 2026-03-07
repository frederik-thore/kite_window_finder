from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ForecastModelName = Literal["ecmwf", "gfs", "icon"]


class ForecastPoint(BaseModel):
    timestamp: datetime
    model: ForecastModelName
    wind_speed_kn: float = Field(ge=0)
    wind_direction_deg: int = Field(ge=0, le=359)
    tide_level_m: float
    air_temp_c: float
    water_temp_c: float
    shortwave_radiation_wm2: float = Field(ge=0)
    cloud_cover_pct: int = Field(ge=0, le=100)
    precipitation_mm: float = Field(ge=0)
    is_daylight: bool


class ObservationPoint(BaseModel):
    timestamp: datetime
    wind_speed_kn: float = Field(ge=0)
    wind_direction_deg: int = Field(ge=0, le=359)


class TimeSeriesPoint(BaseModel):
    forecast: ForecastPoint
    observation: ObservationPoint
