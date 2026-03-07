from pydantic import BaseModel

from app.models.rating import RatingPoint


class TimeSeriesResponse(BaseModel):
    spot_id: str
    from_iso: str
    to_iso: str
    points: list[RatingPoint]
