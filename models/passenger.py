from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Passenger:

    passenger_id: int
    arrival_time: float
    service_start_time: Optional[float] = None
    service_end_time: Optional[float] = None

    @property
    def waiting_time(self) -> Optional[float]:

        if self.service_start_time is None:
            return None
        return self.service_start_time - self.arrival_time