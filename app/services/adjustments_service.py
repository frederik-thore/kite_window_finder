from app.models.adjustment import Adjustment

_ADJUSTMENTS: dict[str, Adjustment] = {}


def get_adjustment(spot_id: str) -> Adjustment:
    return _ADJUSTMENTS.get(spot_id, Adjustment())


def set_adjustment(spot_id: str, adjustment: Adjustment) -> Adjustment:
    _ADJUSTMENTS[spot_id] = adjustment
    return adjustment
