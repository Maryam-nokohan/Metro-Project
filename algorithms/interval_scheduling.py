# algorithms/interval_scheduling.py

from typing import List

from models.train import Train


def select_max_trains(
    trains: List[Train],
) -> List[Train]:
    """
    T3.1 - Classic Interval Scheduling.

    The optimal greedy strategy is:
    1. Sort intervals by earliest departure.
    2. Select an interval if its arrival time is
       not earlier than the departure of the last
       selected interval.

    Complexity:
        Time:  O(n log n)
        Space: O(n)
    """

    if not trains:
        return []

    for train in trains:
        if train.arrival_time > train.departure_time:
            raise ValueError(
                f"بازه زمانی قطار {train.train_id} نامعتبر است."
            )

    sorted_trains = sorted(
        trains,
        key=lambda train: (
            train.departure_time,
            train.arrival_time,
            train.train_id,
        ),
    )

    selected: List[Train] = []
    last_departure = float("-inf")

    for train in sorted_trains:
        if train.arrival_time >= last_departure:
            selected.append(train)
            last_departure = train.departure_time

    return selected