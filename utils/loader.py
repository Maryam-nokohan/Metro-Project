from typing import List, Tuple

from models.graph import Graph
from models.station import Station


def _read_non_comment_lines(
    path: str,
) -> List[str]:
    lines: List[str] = []

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        for raw_line in file:
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            lines.append(line)

    return lines


def load_stations(path: str) -> List[str]:
    return _read_non_comment_lines(path)


def build_graph_from_files(
    stations_path: str,
    edges_path: str,
    directed: bool = False,
) -> Graph:
    graph = Graph(directed=directed)

    for station_id in load_stations(stations_path):
        if not graph.has_station(station_id):
            graph.add_station(Station(station_id))

    for line_number, line in enumerate(
        _read_non_comment_lines(edges_path),
        start=1,
    ):
        parts = [part.strip() for part in line.split("|")]

        if len(parts) not in (4, 5):
            raise ValueError(
                f"فرمت نامعتبر در {edges_path} "
                f"خط {line_number}: {line!r}. "
                "فرمت باید source|destination|distance|time "
                "یا source|destination|distance|time|weight باشد."
            )

        source = parts[0]
        destination = parts[1]

        try:
            distance = float(parts[2])
            time = float(parts[3])
        except ValueError as exc:
            raise ValueError(
                f"مقدار فاصله/زمان نامعتبر در "
                f"{edges_path} خط {line_number}: {line!r}"
            ) from exc

        weight = None

        if len(parts) == 5:
            try:
                weight = float(parts[4])
            except ValueError as exc:
                raise ValueError(
                    f"وزن نامعتبر در " f"{edges_path} خط {line_number}: {line!r}"
                ) from exc

        graph.add_edge(
            source_id=source,
            destination_id=destination,
            distance=distance,
            time=time,
            weight=weight,
        )

    return graph


def load_capacities(
    path: str,
) -> List[Tuple[str, str, float]]:
    capacities = []

    for line_number, line in enumerate(
        _read_non_comment_lines(path),
        start=1,
    ):
        parts = [part.strip() for part in line.split("|")]

        if len(parts) != 3:
            raise ValueError(f"فرمت نامعتبر در {path} " f"خط {line_number}: {line!r}")

        source, destination, capacity_str = parts

        try:
            capacity = float(capacity_str)
        except ValueError as exc:
            raise ValueError(
                f"مقدار ظرفیت نامعتبر در " f"{path} خط {line_number}: {line!r}"
            ) from exc

        if capacity < 0:
            raise ValueError(f"ظرفیت نمی‌تواند منفی باشد: {line!r}")

        capacities.append(
            (
                source,
                destination,
                capacity,
            )
        )

    return capacities


def apply_capacities_from_file(
    graph: Graph,
    path: str,
) -> None:
    for source, destination, capacity in load_capacities(path):
        forward_edge = graph.get_edge(
            source,
            destination,
        )

        if forward_edge is not None:
            forward_edge.capacity = capacity

        backward_edge = graph.get_edge(
            destination,
            source,
        )

        if backward_edge is not None and not backward_edge.directed:
            backward_edge.capacity = capacity
