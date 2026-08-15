import heapq
import itertools
from typing import Any, Optional, Tuple


class PriorityQueue:
    _REMOVED = object()  

    def __init__(self) -> None:
        self._heap: list = []

        self._counter = itertools.count()
        self._entry_finder: dict = {} 

    def push(self, item_id: Any, item: Any, priority: float) -> None:

        if item_id in self._entry_finder:
            self.remove(item_id)
        count = next(self._counter)
        entry = [-priority, count, item_id, item]
        self._entry_finder[item_id] = entry
        heapq.heappush(self._heap, entry)

    def remove(self, item_id: Any) -> bool:
    
        entry = self._entry_finder.pop(item_id, None)
        if entry is None:
            return False
        entry[3] = self._REMOVED
        return True

    def pop(self) -> Tuple[Any, Any, float]:
 
        while self._heap:
            neg_priority, _count, item_id, item = heapq.heappop(self._heap)
            if item is not self._REMOVED and item_id in self._entry_finder:
                del self._entry_finder[item_id]
                return item_id, item, -neg_priority
        raise IndexError("صف اولویت خالی است؛ نمی‌توان pop انجام داد.")

    def peek(self) -> Tuple[Any, Any, float]:

        while self._heap:
            neg_priority, _count, item_id, item = self._heap[0]
            if item is not self._REMOVED and item_id in self._entry_finder:
                return item_id, item, -neg_priority
            heapq.heappop(self._heap)
        raise IndexError("صف اولویت خالی است؛ نمی‌توان peek انجام داد.")

    def is_empty(self) -> bool:
        return len(self._entry_finder) == 0

    def __len__(self) -> int:
        return len(self._entry_finder)