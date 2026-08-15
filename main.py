"""
    python3 main.py
"""

from models.graph import Graph
from models.train import Train, TrainDispatchQueue

from utils.loader import build_graph_from_files, apply_capacities_from_file
from utils.analytics import OperationsLog
from utils.menu import (
    print_header,
    print_menu,
    prompt_choice,
    choose_station,
    prompt_criterion,
    prompt_float,
    prompt_int,
    prompt_text,
    pause,
)

from simulation.passenger_simulator import GateSimulator

from algorithms.bfs import bfs_shortest_path
from algorithms.dfs import dfs_path
from algorithms.dijkstra import dijkstra_shortest_path
from algorithms.kruskal import kruskal
from algorithms.prim import prim
from algorithms.dag_shortest_path import topological_sort, dag_shortest_path_to_target
from algorithms.bellman_ford import bellman_ford
from algorithms.interval_scheduling import select_max_trains
from algorithms.floyd_warshall import floyd_warshall, reconstruct_path as fw_reconstruct_path
from algorithms.max_flow import max_flow
from algorithms.articulation import find_articulation_points_and_bridges
from algorithms.dominating_set import greedy_dominating_set, is_valid_dominating_set
from algorithms.levenshtein import find_closest_station
from algorithms.bidirectional_dijkstra import compare_expanded_nodes


STATIONS_PATH = "data/stations.txt"
EDGES_PATH = "data/edges.txt"
CAPACITY_PATH = "data/capacity.txt"


# ======================================================================
# دور اول: پذیرش اولیه (T1.1 - T1.4)
# ======================================================================
def round1_reachability(graph: Graph) -> None:
    start = choose_station(graph, "ایستگاه مبدأ را انتخاب کنید")
    if start is None:
        return
    goal = choose_station(graph, "ایستگاه مقصد را انتخاب کنید")
    if goal is None:
        return

    path_bfs = bfs_shortest_path(graph, start, goal)
    path_dfs = dfs_path(graph, start, goal)

    print_header("نتیجه‌ی بررسی دسترسی‌پذیری")
    if path_bfs is None:
        print(f"\n❌ هیچ مسیری بین «{start}» و «{goal}» وجود ندارد.")
    else:
        print(f"\n✅ مسیر وجود دارد.")
        print(f"مسیر با BFS (کمترین تعداد ایستگاه): {' -> '.join(path_bfs)}")
        print(f"مسیر با DFS (یک مسیر معتبر، نه لزوماً کوتاه‌ترین): {' -> '.join(path_dfs)}")
    pause()


def round1_shortest_path(graph: Graph) -> None:
    start = choose_station(graph, "ایستگاه مبدأ را انتخاب کنید")
    if start is None:
        return
    goal = choose_station(graph, "ایستگاه مقصد را انتخاب کنید")
    if goal is None:
        return
    criterion = prompt_criterion()

    path, cost = dijkstra_shortest_path(graph, start, goal, criterion)

    print_header("نتیجه‌ی موتور مسیریابی (Dijkstra)")
    if path is None:
        print("\n❌ مسیری بین این دو ایستگاه وجود ندارد.")
    else:
        unit = "کیلومتر" if criterion == "distance" else "دقیقه"
        print(f"\n✅ کوتاه‌ترین مسیر:\n  {' -> '.join(path)}")
        print(f"\nهزینه‌ی کل: {cost:.2f} {unit}")
    pause()


def round1_menu(graph: Graph) -> None:
    options = [
        "بررسی دسترسی‌پذیری بین دو ایستگاه (BFS/DFS) - T1.2",
        "کوتاه‌ترین مسیر بین دو ایستگاه (Dijkstra) - T1.3",
    ]
    while True:
        print_menu("دور اول: پذیرش اولیه", options)
        choice = prompt_choice(len(options))
        if choice == 0:
            return
        if choice == 1:
            round1_reachability(graph)
        elif choice == 2:
            round1_shortest_path(graph)


# ======================================================================
# دور دوم: طراحی زیرساخت‌ها (T2.1 - T2.4)
# ======================================================================
def round2_mst(graph: Graph) -> None:
    criterion = prompt_criterion()
    kruskal_result = kruskal(graph, criterion)
    prim_result = prim(graph, criterion=criterion)

    print_header("کم‌هزینه‌ترین شبکه: مقایسه‌ی Kruskal و Prim")
    print(f"\nKruskal : {len(kruskal_result.edges)} یال, هزینه‌ی کل = {kruskal_result.total_cost:.2f}")
    print(f"Prim    : {len(prim_result.edges)} یال, هزینه‌ی کل = {prim_result.total_cost:.2f}")

    print("\nیال‌های درخت پوشای کمینه (Kruskal):")
    for edge in kruskal_result.edges:
        print(f"  {edge.source}  <->  {edge.destination}   ({edge.get_weight(criterion):.2f})")
    pause()


def _build_demo_express_line() -> Graph:
    """
    زیرشبکه‌ی نمونه‌ی خط اکسپرس یک‌طرفه (T2.3) - یک DAG کوچک، ساخته‌شده
    از زیرمجموعه‌ای از ایستگاه‌های واقعی قم، فقط برای دمو. جدا از گراف
    اصلی نگه داشته می‌شود تا ساختار دوطرفه‌ی گراف اصلی به‌هم نخورد.
    """
    g = Graph(directed=True)
    g.add_edge("ایستگاه ترمینال مسافربری قم", "ایستگاه قلعه کامکار", distance=1.2, time=2, directed=True)
    g.add_edge("ایستگاه قلعه کامکار", "ایستگاه میدان کشاورز", distance=2.5, time=3, directed=True)
    g.add_edge("ایستگاه میدان کشاورز", "ایستگاه میدان مطهری", distance=6, time=5, directed=True)
    g.add_edge("ایستگاه میدان مطهری", "ایستگاه حرم مطهر حضرت معصومه (س)", distance=4, time=1, directed=True)
    return g


def round2_dag(graph: Graph) -> None:
    print_header("خط اکسپرس یک‌طرفه (T2.3)")
    print("\nاین یک زیرشبکه‌ی نمونه از خط اکسپرس یک‌طرفه است (فقط برای دمو،")
    print("جدا از گراف اصلی و روی زیرمجموعه‌ای از ایستگاه‌های واقعی قم):")
    express = _build_demo_express_line()

    order = topological_sort(express)
    print(f"\nترتیب توپولوژیک ایستگاه‌ها:\n  {' -> '.join(order)}")

    start = choose_station(express, "ایستگاه مبدأ روی خط اکسپرس")
    if start is None:
        return
    goal = choose_station(express, "ایستگاه مقصد روی خط اکسپرس")
    if goal is None:
        return
    criterion = prompt_criterion()

    path, cost = dag_shortest_path_to_target(express, start, goal, criterion)
    if path is None:
        print("\n❌ چون خط اکسپرس یک‌طرفه است، مسیری از این مبدأ به این مقصد وجود ندارد.")
        print("   (نکته: مسیر برعکس را هم امتحان کنید - جهت خط را عوض کنید.)")
    else:
        print(f"\n✅ مسیر: {' -> '.join(path)}")
        print(f"هزینه‌ی کل: {cost:.2f}")
    pause()


def round2_bellman_ford(graph: Graph) -> None:
    options = [
        "اجرا روی شبکه‌ی اصلی قم (بررسی وجود چرخه‌ی منفی)",
        "دمو با یک گراف کوچک حاوی چرخه‌ی منفی عمدی",
    ]
    print_menu("بررسی چرخه‌ی منفی و کوتاه‌ترین مسیر (T2.4)", options)
    choice = prompt_choice(len(options))
    if choice == 0:
        return

    if choice == 1:
        start = choose_station(graph, "ایستگاه مبدأ را انتخاب کنید")
        if start is None:
            return
        dist, _parent, negative_cycle = bellman_ford(graph, start, criterion="distance")

        print_header("نتیجه‌ی Bellman-Ford روی شبکه‌ی اصلی")
        if negative_cycle:
            print(f"\n⚠️ چرخه‌ی منفی پیدا شد! یال‌های درگیر: {negative_cycle}")
        else:
            print("\n✅ هیچ چرخه‌ی منفی‌ای در شبکه وجود ندارد؛ فاصله‌ها معتبرند.")
            print(f"\nنمونه‌ای از فاصله‌ی محاسبه‌شده از «{start}»:")
            for station_id, distance in list(dist.items())[:5]:
                print(f"  {station_id}: {distance:.2f}")
    else:
        demo = Graph(directed=True)
        demo.add_edge("A", "B", distance=1, time=1, weight=1)
        demo.add_edge("B", "C", distance=1, time=1, weight=-3)
        demo.add_edge("C", "A", distance=1, time=1, weight=1)

        print_header("دمو: گراف حاوی چرخه‌ی منفی عمدی")
        print("\nA -> B (وزن=+1)   B -> C (وزن=-3)   C -> A (وزن=+1)")
        print("مجموع وزن چرخه‌ی A->B->C->A برابر 1-3+1 = -1 است (منفی).")

        _dist, _parent, negative_cycle = bellman_ford(demo, "A", criterion="weight")
        if negative_cycle:
            print(f"\n✅ الگوریتم به‌درستی چرخه‌ی منفی را تشخیص داد: {negative_cycle}")
        else:
            print("\n❌ چرخه‌ی منفی تشخیص داده نشد (نتیجه‌ی غیرمنتظره برای این دمو).")
    pause()


def round2_menu(graph: Graph) -> None:
    options = [
        "طراحی کم‌هزینه‌ترین شبکه - مقایسه‌ی Kruskal/Prim (T2.1, T2.2)",
        "کوتاه‌ترین مسیر روی خط اکسپرس یک‌طرفه (T2.3)",
        "بررسی چرخه‌ی منفی (T2.4)",
    ]
    while True:
        print_menu("دور دوم: طراحی زیرساخت‌ها", options)
        choice = prompt_choice(len(options))
        if choice == 0:
            return
        if choice == 1:
            round2_mst(graph)
        elif choice == 2:
            round2_dag(graph)
        elif choice == 3:
            round2_bellman_ford(graph)


# ======================================================================
# دور سوم: عملیات‌های روزانه‌ی مترو (T3.1 - T3.4)
# ======================================================================
def round3_interval_scheduling() -> None:
    options = ["استفاده از داده‌ی نمونه", "وارد کردن دستی قطارها"]
    print_menu("تخصیص بیشینه‌ی قطارها به یک سکوی مشترک (T3.1)", options)
    choice = prompt_choice(len(options))
    if choice == 0:
        return

    if choice == 1:
        sample = [
            ("A", 1, 4), ("B", 3, 5), ("C", 0, 6), ("D", 5, 7),
            ("E", 3, 9), ("F", 5, 9), ("G", 6, 10), ("H", 8, 11),
            ("I", 8, 12), ("J", 2, 14), ("K", 12, 16),
        ]
        trains = [Train(train_id, arrival, departure) for train_id, arrival, departure in sample]
    else:
        count = prompt_int("چند قطار می‌خواهید وارد کنید؟", default=3)
        trains = []
        for i in range(1, count + 1):
            print(f"\nقطار شماره‌ی {i}:")
            arrival = prompt_float("  زمان ورود به سکو")
            departure = prompt_float("  زمان خروج از سکو")
            trains.append(Train(f"T{i}", arrival, departure))

    print("\nلیست قطارهای ورودی (بازه‌ی اشغال سکو):")
    for train in trains:
        print(f"  {train.train_id}: [{train.arrival_time}, {train.departure_time})")

    selected = select_max_trains(trains)
    print_header("نتیجه‌ی زمان‌بندی")
    print(f"\n✅ بیشترین تعداد قطار قابل‌سرویس‌دهی بدون تداخل زمانی: {len(selected)}")
    print("قطارهای انتخاب‌شده: " + ", ".join(t.train_id for t in selected))
    pause()


def round3_dispatch_queue() -> None:
    print_header("مدیریت صف اعزام قطارها بر اساس اولویت (T3.2)")
    sample = [
        Train("Normal-1", 0, 10, delay_minutes=3),
        Train("Delayed", 0, 10, delay_minutes=20),
        Train("Emergency", 0, 10, delay_minutes=0, is_emergency=True),
        Train("Normal-2", 0, 10, delay_minutes=1),
    ]

    queue = TrainDispatchQueue()
    print("\nقطارهای اضافه‌شده به صف:")
    for train in sample:
        queue.add_train(train)
        print(f"  + {train.train_id}  (تأخیر={train.delay_minutes} دقیقه, اضطراری={train.is_emergency})")

    print("\nترتیب اعزام (بالاترین اولویت اول):")
    order = 1
    while not queue.is_empty():
        train = queue.dispatch_next()
        print(f"  {order}) {train.train_id}")
        order += 1
    pause()


def round3_analytics_and_simulation(graph: Graph) -> None:
    """
    این بخش T3.3 (تحلیل داده‌های بهره‌برداری) و T3.4 (شبیه‌سازی ورود
    مسافران) را با هم ترکیب می‌کند: برای چند «روز» فرضی، ورود مسافران
    به تعدادی از ایستگاه‌ها شبیه‌سازی می‌شود و نتیجه در OperationsLog
    ثبت می‌گردد؛ سپس پرس‌وجوهای تحلیلی روی همین داده‌ی تولیدشده اجرا
    می‌شوند (دقیقاً همان معماری «سامانه‌ی یکپارچه» که سند پروژه خواسته).
    """
    print_header("شبیه‌سازی روزانه + تحلیل داده‌های بهره‌برداری (T3.3 + T3.4)")
    num_days = prompt_int("تعداد روزهای شبیه‌سازی", default=3)
    sample_stations = graph.station_ids()[:6]

    log = OperationsLog()
    print(f"\nدر حال شبیه‌سازی {num_days} روز برای {len(sample_stations)} ایستگاه...")

    for day in range(1, num_days + 1):
        date_label = f"روز {day}"
        for station_id in sample_stations:
            simulator = GateSimulator(num_gates=2, service_time_seconds=4)
            passengers = simulator.generate_arrivals(duration_minutes=60, avg_arrivals_per_minute=1.5)
            simulator.simulate(passengers)
            log.record_trip(date_label, station_id, len(passengers))

    print(f"✅ {log.total_records()} رکورد سفر ثبت شد.")
    print(f"\nمیانگین سفر روزانه‌ی کل شبکه: {log.average_daily_trips():.1f} نفر")

    k = prompt_int("برای دیدن k امین ایستگاه پرتردد، مقدار k را وارد کنید", default=1)
    result = log.kth_busiest_station(k)
    if result:
        print(f"\n{k} امین ایستگاه پرتردد: «{result[0]}» با {result[1]} سفر")
    else:
        print("\n❌ مقدار k نامعتبر است (باید بین ۱ و تعداد ایستگاه‌های نمونه باشد).")
    pause()


def round3_menu(graph: Graph) -> None:
    options = [
        "تخصیص بیشینه‌ی قطارها به یک سکوی مشترک (T3.1)",
        "مدیریت صف اعزام قطارها (T3.2)",
        "شبیه‌سازی مسافران + تحلیل داده‌های بهره‌برداری (T3.3 + T3.4)",
    ]
    while True:
        print_menu("دور سوم: عملیات‌های روزانه‌ی مترو", options)
        choice = prompt_choice(len(options))
        if choice == 0:
            return
        if choice == 1:
            round3_interval_scheduling()
        elif choice == 2:
            round3_dispatch_queue()
        elif choice == 3:
            round3_analytics_and_simulation(graph)


# ======================================================================
# دور چهارم: تحلیل و ارزیابی عملکرد شبکه (T4.1 - T4.5)
# ======================================================================
def round4_floyd_warshall(graph: Graph) -> None:
    criterion = prompt_criterion()
    print("\nدر حال پیش‌محاسبه‌ی ماتریس کامل کوتاه‌ترین مسیرها...")
    station_ids, dist_matrix, next_hop = floyd_warshall(graph, criterion)

    start = choose_station(graph, "ایستگاه مبدأ را انتخاب کنید")
    if start is None:
        return
    goal = choose_station(graph, "ایستگاه مقصد را انتخاب کنید")
    if goal is None:
        return

    path = fw_reconstruct_path(station_ids, next_hop, start, goal)
    index_of = {sid: i for i, sid in enumerate(station_ids)}
    cost = dist_matrix[index_of[start]][index_of[goal]]

    print_header("نتیجه‌ی Floyd-Warshall")
    print(f"\n✅ کوتاه‌ترین مسیر (از ماتریس پیش‌محاسبه‌شده): {' -> '.join(path)}")
    print(f"هزینه: {cost:.2f}")
    pause()


def round4_max_flow(graph: Graph) -> None:
    source = choose_station(graph, "ایستگاه مبدأ (منبع جریان مسافر)")
    if source is None:
        return
    sink = choose_station(graph, "ایستگاه مقصد (چاهک جریان مسافر)")
    if sink is None:
        return

    flow_value = max_flow(graph, source, sink)
    print_header("نتیجه‌ی ظرفیت‌سنجی شبکه (Max-Flow)")
    print(f"\n✅ بیشینه‌ی جریان قابل‌انتقال: {flow_value:.0f} نفر بر ساعت")
    pause()


def round4_articulation(graph: Graph) -> None:
    points, bridges = find_articulation_points_and_bridges(graph)

    print_header("ایستگاه‌های بحرانی و مسیرهای بحرانی (T4.3)")
    print(f"\nتعداد ایستگاه‌های بحرانی (نقاط برشی): {len(points)}")
    for station_id in sorted(points):
        print(f"  - {station_id}")

    print(f"\nتعداد مسیرهای بحرانی (پل): {len(bridges)}")
    for source, destination in bridges:
        print(f"  - {source}  <->  {destination}")
    pause()


def round4_dominating_set(graph: Graph) -> None:
    solution = greedy_dominating_set(graph)
    valid = is_valid_dominating_set(graph, solution)

    print_header("استقرار تیم‌های امداد - تقریبی (T4.4، امتیازی)")
    print(f"\n✅ تعداد ایستگاه‌های پیشنهادی برای استقرار: {len(solution)} از {graph.num_stations()}")
    for station_id in solution:
        print(f"  - {station_id}")
    print(f"\nاعتبارسنجی: {'✅ همه‌ی ایستگاه‌ها پوشش داده شدند' if valid else '❌ خطا در الگوریتم'}")
    pause()


def round4_levenshtein(graph: Graph) -> None:
    query = prompt_text("نام ایستگاه را وارد کنید (حتی اگر غلط تایپی داشته باشد)")
    results = find_closest_station(query, graph.station_ids(), max_results=3)

    print_header("نتیجه‌ی جست‌وجوی تایپی‌تحمل‌پذیر")
    print("\nنزدیک‌ترین نام‌های ایستگاه:")
    for name, distance in results:
        print(f"  {name}   (فاصله‌ی ویرایشی = {distance})")
    pause()


def round4_menu(graph: Graph) -> None:
    options = [
        "پیش‌محاسبه‌ی کوتاه‌ترین مسیر بین همه‌ی ایستگاه‌ها (Floyd-Warshall) - T4.1",
        "ظرفیت‌سنجی شبکه در ساعات اوج (Max-Flow) - T4.2",
        "شناسایی ایستگاه‌های بحرانی (نقاط برشی و پل‌ها) - T4.3",
        "استقرار تیم‌های امداد - تقریبی (امتیازی) - T4.4",
        "جست‌وجوی نام ایستگاه با تحمل خطای تایپی - T4.5",
    ]
    while True:
        print_menu("دور چهارم: تحلیل و ارزیابی عملکرد شبکه", options)
        choice = prompt_choice(len(options))
        if choice == 0:
            return
        if choice == 1:
            round4_floyd_warshall(graph)
        elif choice == 2:
            round4_max_flow(graph)
        elif choice == 3:
            round4_articulation(graph)
        elif choice == 4:
            round4_dominating_set(graph)
        elif choice == 5:
            round4_levenshtein(graph)


# ======================================================================
# دور پنجم: نوآوری - امتیازی (Bidirectional Dijkstra)
# ======================================================================
def round5_bidirectional(graph: Graph) -> None:
    start = choose_station(graph, "ایستگاه مبدأ را انتخاب کنید")
    if start is None:
        return
    goal = choose_station(graph, "ایستگاه مقصد را انتخاب کنید")
    if goal is None:
        return
    criterion = prompt_criterion()

    result = compare_expanded_nodes(graph, start, goal, criterion)
    uni = result["unidirectional"]
    bi = result["bidirectional"]

    print_header("مقایسه‌ی Dijkstra یک‌طرفه و دوطرفه")
    print(f"\nDijkstra یک‌طرفه : هزینه={uni['cost']:.2f}   گره‌های بازشده={uni['expanded_nodes']}")
    print(f"Dijkstra دوطرفه  : هزینه={bi['cost']:.2f}   گره‌های بازشده={bi['expanded_nodes']}")
    print(f"\nهزینه‌ها برابرند؟ {'✅ بله (درستی الگوریتم تأیید شد)' if result['costs_match'] else '❌ خیر!'}")

    if bi["expanded_nodes"] < uni["expanded_nodes"]:
        saved = uni["expanded_nodes"] - bi["expanded_nodes"]
        print(f"جست‌وجوی دوطرفه {saved} گره کمتر باز کرد.")
    pause()


def round5_menu(graph: Graph) -> None:
    options = ["مقایسه‌ی Dijkstra یک‌طرفه و دوطرفه"]
    while True:
        print_menu("دور پنجم: نوآوری (امتیازی)", options)
        choice = prompt_choice(len(options))
        if choice == 0:
            return
        if choice == 1:
            round5_bidirectional(graph)


# ======================================================================
# منوی اصلی
# ======================================================================
def load_system() -> Graph:
    graph = build_graph_from_files(STATIONS_PATH, EDGES_PATH)
    apply_capacities_from_file(graph, CAPACITY_PATH)
    return graph


def main() -> None:
    print_header("سامانه‌ی مسیریابی متروی قم  -  UrbanPulse Technical Study")
    print("\nدر حال بارگذاری داده‌های شبکه...")
    graph = load_system()
    print(f"✅ {graph.num_stations()} ایستگاه و {graph.num_edges()} مسیر با موفقیت بارگذاری شد.")

    main_options = [
        "دور اول: پذیرش اولیه (مسیریابی پایه)",
        "دور دوم: طراحی زیرساخت‌ها (MST / خط اکسپرس / چرخه‌ی منفی)",
        "دور سوم: عملیات‌های روزانه‌ی مترو",
        "دور چهارم: تحلیل و ارزیابی عملکرد شبکه",
        "دور پنجم: نوآوری (امتیازی)",
    ]

    while True:
        print_menu("منوی اصلی", main_options)
        choice = prompt_choice(len(main_options))
        if choice == 0:
            print("\nخداحافظ 👋")
            return
        if choice == 1:
            round1_menu(graph)
        elif choice == 2:
            round2_menu(graph)
        elif choice == 3:
            round3_menu(graph)
        elif choice == 4:
            round4_menu(graph)
        elif choice == 5:
            round5_menu(graph)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nبرنامه توسط کاربر متوقف شد.")