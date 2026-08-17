from __future__ import annotations
from typing import Any, Dict, Optional


class Station:
    __slots__ = ("station_id", "name", "metadata")

    def __init__(
        self,
        station_id: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not station_id:
            raise ValueError("station_id نمی‌تواند خالی باشد.")

        self.station_id: str = station_id
        self.name: str = name if name else station_id
        self.metadata: Dict[str, Any] = metadata if metadata is not None else {}

    def __repr__(self) -> str:
        return f"Station(id={self.station_id!r}, name={self.name!r})"

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:

        if not isinstance(other, Station):
            return NotImplemented
        return self.station_id == other.station_id

    def __hash__(self) -> int:

        return hash(self.station_id)
