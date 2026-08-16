from __future__ import annotations
import heapq
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class TripRecord:
    date: str
    station_id: str
    trip_count: int = 1


class OperationsLog:
    def __init__(self) -> None:
        self._records: List[TripRecord] = []

    def record_trip(self, date: str, station_id: str, count: int = 1) -> None:

        self._records.append(
            TripRecord(date=date, station_id=station_id, trip_count=count)
        )

    def average_daily_trips(self) -> float:

        if not self._records:
            return 0.0

        daily_totals: Dict[str, int] = {}
        for record in self._records:
            daily_totals[record.date] = (
                daily_totals.get(record.date, 0) + record.trip_count
            )

        return sum(daily_totals.values()) / len(daily_totals)

    def kth_busiest_station(self, k: int) -> Optional[Tuple[str, int]]:

        totals: Dict[str, int] = {}
        for record in self._records:
            totals[record.station_id] = (
                totals.get(record.station_id, 0) + record.trip_count
            )

        if k < 1 or k > len(totals):
            return None

        top_k = heapq.nlargest(k, totals.items(), key=lambda item: item[1])
        return top_k[k - 1]

    def total_records(self) -> int:
        return len(self._records)
