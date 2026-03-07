from pydantic import BaseModel, Field

from app.models.weather import ForecastModelName


class ModelSkillEntry(BaseModel):
    model: ForecastModelName
    mae_wind_kn: float = Field(ge=0)
    mae_dir_deg: float = Field(ge=0)
    kiteable_hit_rate: float = Field(ge=0, le=1)
    model_skill: float = Field(ge=0, le=1)


class ModelSkillResponse(BaseModel):
    spot_id: str
    window_days: int
    active_model: ForecastModelName
    entries: list[ModelSkillEntry]
