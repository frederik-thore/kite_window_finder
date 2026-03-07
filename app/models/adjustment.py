from pydantic import BaseModel, Field


class Adjustment(BaseModel):
    wind_speed_offset_kn: float = Field(default=0.0, ge=-15, le=15)
    wind_direction_offset_deg: int = Field(default=0, ge=-180, le=180)


class AdjustmentResponse(BaseModel):
    spot_id: str
    adjustment: Adjustment
