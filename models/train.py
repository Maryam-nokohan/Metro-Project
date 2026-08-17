from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from utils.priority_queue import PriorityQueue


@dataclass
class Train:
    train_id: str
    arrival_time: float
    departure_time: float
    delay_minutes: float = 0.0
    is_emergency: bool = False

    def __post_init__(self) -> None:
        if not self.train_id:
            raise ValueError("شناسه قطار نمی‌تواند خالی باشد.")

        if self.arrival_time < 0:
            raise ValueError("زمان ورود نمی‌تواند منفی باشد.")

        if self.departure_time < self.arrival_time:
            raise ValueError("زمان خروج باید بزرگ‌تر یا مساوی زمان ورود باشد.")

        if self.delay_minutes < 0:
            raise ValueError("میزان تأخیر نمی‌تواند منفی باشد.")

    def overlaps(self, other: "Train") -> bool:
        return (
            self.arrival_time < other.departure_time
            and other.arrival_time < self.departure_time
        )

    def priority_score(self) -> float:
        if self.is_emergency:
            return 1_000_000.0 + self.delay_minutes

        return self.delay_minutes


class TrainDispatchQueue:
    def __init__(self) -> None:
        self._queue = PriorityQueue()
        self._trains: dict[str, Train] = {}

    def add_train(self, train: Train) -> None:
        self._trains[train.train_id] = train

        self._queue.push(
            train.train_id,
            train,
            train.priority_score(),
        )

    def remove_train(self, train_id: str) -> bool:
        removed = self._queue.remove(train_id)

        if removed:
            self._trains.pop(train_id, None)

        return removed

    def dispatch_next(self) -> Optional[Train]:
        if self._queue.is_empty():
            return None

        train_id, train, _priority = self._queue.pop()

        self._trains.pop(train_id, None)

        return train

    def peek_next(self) -> Optional[Train]:
        if self._queue.is_empty():
            return None

        _train_id, train, _priority = self._queue.peek()

        return train

    def is_empty(self) -> bool:
        return self._queue.is_empty()

    def __len__(self) -> int:
        return len(self._queue)
