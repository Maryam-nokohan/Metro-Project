from __future__ import annotations
import random
from typing import List, Optional

from models.passenger import Passenger


class GateSimulator:
    def __init__(
        self,
        num_gates: int,
        service_time_seconds: float = 3.0,
        seed: Optional[int] = None,
    ) -> None:
        if num_gates < 1:
            raise ValueError("num_gates باید حداقل ۱ باشد.")
        self.num_gates = num_gates
        self.service_time_minutes = service_time_seconds / 60.0
        self._rng = random.Random(seed)

    def generate_arrivals(
        self, duration_minutes: float, avg_arrivals_per_minute: float
    ) -> List[Passenger]:

        if avg_arrivals_per_minute <= 0:
            return []

        passengers: List[Passenger] = []
        current_time = 0.0
        next_id = 1

        while True:
            interarrival = self._rng.expovariate(avg_arrivals_per_minute)
            current_time += interarrival
            if current_time >= duration_minutes:
                break
            passengers.append(
                Passenger(passenger_id=next_id, arrival_time=current_time)
            )
            next_id += 1

        return passengers

    def simulate(self, passengers: List[Passenger]) -> List[Passenger]:

        gate_free_at = [0.0] * self.num_gates

        for passenger in sorted(passengers, key=lambda p: p.arrival_time):
            gate_index = min(range(self.num_gates), key=lambda i: gate_free_at[i])
            start_time = max(passenger.arrival_time, gate_free_at[gate_index])

            passenger.service_start_time = start_time
            passenger.service_end_time = start_time + self.service_time_minutes
            gate_free_at[gate_index] = passenger.service_end_time

        return passengers

    @staticmethod
    def average_waiting_time(passengers: List[Passenger]) -> float:

        waits = [p.waiting_time for p in passengers if p.waiting_time is not None]
        return sum(waits) / len(waits) if waits else 0.0

    @staticmethod
    def max_waiting_time(passengers: List[Passenger]) -> float:

        waits = [p.waiting_time for p in passengers if p.waiting_time is not None]
        return max(waits) if waits else 0.0
