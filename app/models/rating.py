from datetime import datetime

from pydantic import BaseModel, Field

from app.models.weather import ForecastPoint, ObservationPoint


class RatingExplanation(BaseModel):
    hard_gates_triggered: list[str]
    components: dict[str, float]
    weighted_score: float = Field(ge=0, le=1)


class RatingPoint(BaseModel):
    timestamp: datetime
    stars: float = Field(ge=0, le=5)
    forecast: ForecastPoint
    observation: ObservationPoint | None
    neoprene_recommendation: str
    explanation: RatingExplanation


class RatingDayResponse(BaseModel):
    spot_id: str
    date: str
    points: list[RatingPoint]


class ExplainResponse(BaseModel):
    spot_id: str
    point: RatingPoint
