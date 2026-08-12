"""
tests/test_daily_operations.py
--------------------------------
تست‌های واحد برای دور سوم پروژه (عملیات‌های روزانه‌ی مترو):
    TestIntervalScheduling : T3.1 - تخصیص بیشینه‌ی قطارها به یک سکو
    TestPriorityQueue       : زیرساخت عمومی مورد استفاده در T3.2
    TestTrainDispatchQueue  : T3.2 - مدیریت صف اعزام قطارها
    TestOperationsLog       : T3.3 - تحلیل داده‌های بهره‌برداری
    TestGateSimulator       : T3.4 - شبیه‌سازی ورود مسافران

اجرا از ریشه‌ی پروژه:
    python3 -m unittest tests/test_daily_operations.py -v
"""

import unittest

from models.train import Train, TrainDispatchQueue
from models.passenger import Passenger
from algorithms.interval_scheduling import select_max_trains
from utils.priority_queue import PriorityQueue
from utils.analytics import OperationsLog
from simulation.passenger_simulator import GateSimulator


# ======================================================================
# T3.1 - Interval Scheduling
# ======================================================================
class TestIntervalScheduling(unittest.TestCase):
    def test_classic_overlap_example(self):
        # سه قطار کاملاً هم‌پوشان؛ فقط یکی قابل انتخاب است
        trains = [
            Train("T1", arrival_time=0, departure_time=10),
            Train("T2", arrival_time=2, departure_time=8),
            Train("T3", arrival_time=5, departure_time=15),
        ]
        selected = select_max_trains(trains)
        self.assertEqual(len(selected), 1)

    def test_non_overlapping_all_selected(self):
        trains = [
            Train("T1", arrival_time=0, departure_time=5),
            Train("T2", arrival_time=5, departure_time=10),
            Train("T3", arrival_time=10, departure_time=15),
        ]
        selected = select_max_trains(trains)
        self.assertEqual(len(selected), 3)

    def test_greedy_picks_maximum_not_just_any(self):
        # این نمونه‌ی کلاسیک است که در آن انتخاب حریصانه‌ی نادرست
        # (مثلاً بر اساس کوتاه‌ترین بازه) جواب غلط می‌دهد، ولی مرتب‌سازی
        # بر اساس departure_time جواب درست (۴ قطار) را می‌دهد.
        trains = [
            Train("A", 1, 4),
            Train("B", 3, 5),
            Train("C", 0, 6),
            Train("D", 5, 7),
            Train("E", 3, 9),
            Train("F", 5, 9),
            Train("G", 6, 10),
            Train("H", 8, 11),
            Train("I", 8, 12),
            Train("J", 2, 14),
            Train("K", 12, 16),
        ]
        selected = select_max_trains(trains)
        self.assertEqual(len(selected), 4)  # A, B/D, G/F, K (بهینه ۴ تاست)

    def test_empty_input(self):
        self.assertEqual(select_max_trains([]), [])


# ======================================================================
# PriorityQueue (زیرساخت عمومی T3.2)
# ======================================================================
class TestPriorityQueue(unittest.TestCase):
    def test_pop_returns_highest_priority_first(self):
        pq = PriorityQueue()
        pq.push("low", "low-item", priority=1)
        pq.push("high", "high-item", priority=10)
        pq.push("mid", "mid-item", priority=5)

        first = pq.pop()
        second = pq.pop()
        third = pq.pop()

        self.assertEqual(first[0], "high")
        self.assertEqual(second[0], "mid")
        self.assertEqual(third[0], "low")

    def test_remove_before_pop(self):
        pq = PriorityQueue()
        pq.push("a", "A", priority=1)
        pq.push("b", "B", priority=2)

        removed = pq.remove("b")
        self.assertTrue(removed)
        self.assertEqual(len(pq), 1)

        item_id, _item, _priority = pq.pop()
        self.assertEqual(item_id, "a")

    def test_remove_unknown_returns_false(self):
        pq = PriorityQueue()
        self.assertFalse(pq.remove("not_here"))

    def test_pop_empty_raises(self):
        pq = PriorityQueue()
        with self.assertRaises(IndexError):
            pq.pop()

    def test_push_same_id_twice_replaces(self):
        pq = PriorityQueue()
        pq.push("x", "old", priority=1)
        pq.push("x", "new", priority=99)
        self.assertEqual(len(pq), 1)
        item_id, item, priority = pq.pop()
        self.assertEqual(item, "new")
        self.assertEqual(priority, 99)


# ======================================================================
# T3.2 - TrainDispatchQueue
# ======================================================================
class TestTrainDispatchQueue(unittest.TestCase):
    def test_more_delayed_train_dispatched_first(self):
        q = TrainDispatchQueue()
        q.add_train(Train("A", 0, 10, delay_minutes=2))
        q.add_train(Train("B", 0, 10, delay_minutes=15))
        q.add_train(Train("C", 0, 10, delay_minutes=5))

        first = q.dispatch_next()
        self.assertEqual(first.train_id, "B")

    def test_emergency_train_always_first(self):
        q = TrainDispatchQueue()
        q.add_train(Train("Normal-High-Delay", 0, 10, delay_minutes=1000))
        q.add_train(Train("Emergency", 0, 10, delay_minutes=0, is_emergency=True))

        first = q.dispatch_next()
        self.assertEqual(first.train_id, "Emergency")

    def test_remove_train(self):
        q = TrainDispatchQueue()
        q.add_train(Train("A", 0, 10, delay_minutes=5))
        removed = q.remove_train("A")
        self.assertTrue(removed)
        self.assertTrue(q.is_empty())

    def test_dispatch_from_empty_returns_none(self):
        q = TrainDispatchQueue()
        self.assertIsNone(q.dispatch_next())

    def test_peek_does_not_remove(self):
        q = TrainDispatchQueue()
        q.add_train(Train("A", 0, 10, delay_minutes=5))
        peeked = q.peek_next()
        self.assertEqual(peeked.train_id, "A")
        self.assertEqual(len(q), 1)


# ======================================================================
# T3.3 - OperationsLog
# ======================================================================
class TestOperationsLog(unittest.TestCase):
    def setUp(self):
        self.log = OperationsLog()
        self.log.record_trip("2026-08-01", "Station-A", 100)
        self.log.record_trip("2026-08-01", "Station-B", 50)
        self.log.record_trip("2026-08-02", "Station-A", 80)
        self.log.record_trip("2026-08-02", "Station-C", 200)

    def test_average_daily_trips(self):
        # روز ۱: ۱۰۰+۵۰=۱۵۰   روز ۲: ۸۰+۲۰۰=۲۸۰   میانگین = ۲۱۵
        self.assertAlmostEqual(self.log.average_daily_trips(), 215.0)

    def test_average_daily_trips_empty_log(self):
        empty_log = OperationsLog()
        self.assertEqual(empty_log.average_daily_trips(), 0.0)

    def test_kth_busiest_station(self):
        # مجموع کل: A=180, B=50, C=200  ->  ترتیب نزولی: C(200), A(180), B(50)
        self.assertEqual(self.log.kth_busiest_station(1), ("Station-C", 200))
        self.assertEqual(self.log.kth_busiest_station(2), ("Station-A", 180))
        self.assertEqual(self.log.kth_busiest_station(3), ("Station-B", 50))

    def test_kth_busiest_station_invalid_k(self):
        self.assertIsNone(self.log.kth_busiest_station(0))
        self.assertIsNone(self.log.kth_busiest_station(100))


# ======================================================================
# T3.4 - GateSimulator
# ======================================================================
class TestGateSimulator(unittest.TestCase):
    def test_generate_arrivals_within_duration_and_sorted(self):
        sim = GateSimulator(num_gates=2, seed=42)
        passengers = sim.generate_arrivals(duration_minutes=30, avg_arrivals_per_minute=2)

        self.assertTrue(len(passengers) > 0)
        for p in passengers:
            self.assertLess(p.arrival_time, 30)
        arrival_times = [p.arrival_time for p in passengers]
        self.assertEqual(arrival_times, sorted(arrival_times))

    def test_generate_arrivals_is_reproducible_with_seed(self):
        sim1 = GateSimulator(num_gates=1, seed=123)
        sim2 = GateSimulator(num_gates=1, seed=123)
        p1 = sim1.generate_arrivals(20, 1)
        p2 = sim2.generate_arrivals(20, 1)
        self.assertEqual(
            [p.arrival_time for p in p1], [p.arrival_time for p in p2]
        )

    def test_simulate_fills_service_times(self):
        sim = GateSimulator(num_gates=1, service_time_seconds=60, seed=1)
        passengers = [Passenger(1, arrival_time=0), Passenger(2, arrival_time=0.1)]
        result = sim.simulate(passengers)

        self.assertEqual(result[0].service_start_time, 0)
        self.assertEqual(result[0].service_end_time, 1)  # ۶۰ ثانیه = ۱ دقیقه
        # مسافر دوم باید منتظر بماند تا مسافر اول تمام شود (گیت یکی است)
        self.assertEqual(result[1].service_start_time, 1)

    def test_more_gates_reduce_average_waiting_time(self):
        sim_one_gate = GateSimulator(num_gates=1, service_time_seconds=10, seed=7)
        sim_many_gates = GateSimulator(num_gates=5, service_time_seconds=10, seed=7)

        arrivals = sim_one_gate.generate_arrivals(duration_minutes=10, avg_arrivals_per_minute=3)
        arrivals_copy = [Passenger(p.passenger_id, p.arrival_time) for p in arrivals]

        result_one = sim_one_gate.simulate(arrivals)
        result_many = sim_many_gates.simulate(arrivals_copy)

        wait_one = GateSimulator.average_waiting_time(result_one)
        wait_many = GateSimulator.average_waiting_time(result_many)

        self.assertGreaterEqual(wait_one, wait_many)

    def test_invalid_num_gates_raises(self):
        with self.assertRaises(ValueError):
            GateSimulator(num_gates=0)


if __name__ == "__main__":
    unittest.main()
