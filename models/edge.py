from __future__ import annotations
from typing import Optional


class Edge:
 
    __slots__ = (
        "source",
        "destination",
        "distance",
        "time",
        "directed",
        "weight",
        "capacity",
    )

    def __init__(
        self,
        source: str,
        destination: str,
        distance: float = 0.0,
        time: float = 0.0,
        directed: bool = False,
        weight: Optional[float] = None,
        capacity: Optional[float] = None,
    ) -> None:
        if source == destination:
            raise ValueError("یال حلقه‌ای (source == destination) مجاز نیست.")

        self.source: str = source
        self.destination: str = destination
        self.distance: float = float(distance)
        self.time: float = float(time)
        self.directed: bool = directed

        self.weight: Optional[float] = weight
        self.capacity: Optional[float] = capacity

    def get_weight(self, criterion: str = "distance") -> float:

        if criterion == "distance":
            return self.distance
        if criterion == "time":
            return self.time
        if criterion == "weight":
            return self.weight if self.weight is not None else self.distance
        raise ValueError(
            f"معیار نامعتبر: {criterion!r} (باید یکی از distance/time/weight باشد)"
        )

    def reversed(self) -> "Edge":

        return Edge(
            source=self.destination,
            destination=self.source,
            distance=self.distance,
            time=self.time,
            directed=self.directed,
            weight=self.weight,
            capacity=self.capacity,
        )


    def __repr__(self) -> str:
        arrow = "->" if self.directed else "<->"
        return (
            f"Edge({self.source!r} {arrow} {self.destination!r}, "
            f"distance={self.distance}, time={self.time})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Edge):
            return NotImplemented
        return (
            self.source == other.source
            and self.destination == other.destination
            and self.directed == other.directed
        )

    def __hash__(self) -> int:
        return hash((self.source, self.destination, self.directed))