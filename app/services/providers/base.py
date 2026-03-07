from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from app.models.spot import Spot
from app.models.weather import ForecastModelName, ForecastPoint, ObservationPoint


class ForecastProvider(Protocol):
    def hourly_forecast(
        self,
        spot: Spot,
        dt_from: datetime,
        dt_to: datetime,
        model: ForecastModelName,
    ) -> Sequence[ForecastPoint]: ...


class ObservationProvider(Protocol):
    def hourly_observations(
        self,
        spot: Spot,
        dt_from: datetime,
        dt_to: datetime,
    ) -> Sequence[ObservationPoint]: ...
