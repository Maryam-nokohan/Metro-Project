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

    def overlaps(self, other: "Train") -> bool:
  
        return self.arrival_time < other.departure_time and other.arrival_time < self.departure_time

    def priority_score(self) -> float:
 
        score = float(self.delay_minutes)
        if self.is_emergency:
            score += 1_000_000.0 
        return score

    def __repr__(self) -> str:
        return (
            f"Train(id={self.train_id!r}, window=[{self.arrival_time}, "
            f"{self.departure_time}], delay={self.delay_minutes}, "
            f"emergency={self.is_emergency})"
        )


class TrainDispatchQueue:

    def __init__(self) -> None:
        self._queue: PriorityQueue = PriorityQueue()
        self._trains: dict[str, Train] = {}

    def add_train(self, train: Train) -> None:
        
        self._trains[train.train_id] = train
        self._queue.push(train.train_id, train, train.priority_score())

    def remove_train(self, train_id: str) -> bool:

        removed = self._queue.remove(train_id)
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