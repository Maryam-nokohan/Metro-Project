from typing import List

from models.train import Train


def select_max_trains(trains: List[Train]) -> List[Train]:

    sorted_trains = sorted(trains, key=lambda t: t.departure_time)

    selected: List[Train] = []
    last_departure = float("-inf")

    for train in sorted_trains:
        if train.arrival_time >= last_departure:
            selected.append(train)
            last_departure = train.departure_time

    return selected
