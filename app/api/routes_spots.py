from fastapi import APIRouter

from app.models.spot import Spot
from app.services.spots_service import list_spots

router = APIRouter(prefix="/spots", tags=["spots"])


@router.get("", response_model=list[Spot])
def read_spots() -> list[Spot]:
    return list_spots()
