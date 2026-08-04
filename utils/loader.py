from typing import List

from models.graph import Graph
from models.station import Station


def _read_non_comment_lines(path: str) -> List[str]:

    lines: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)
    return lines


def load_stations(path: str) -> List[str]:

    return _read_non_comment_lines(path)


def build_graph_from_files(
    stations_path: str, edges_path: str, directed: bool = False
) -> Graph:

    graph = Graph(directed=directed)

    for station_id in load_stations(stations_path):
        if not graph.has_station(station_id):
            graph.add_station(Station(station_id))

    for line_number, line in enumerate(_read_non_comment_lines(edges_path), start=1):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 4:
            raise ValueError(
                f"فرمت نامعتبر در {edges_path} خط {line_number}: {line!r} "
                f"(باید ۴ فیلد با جداکننده '|' داشته باشد)"
            )

        source, destination, distance_str, time_str = parts
        try:
            distance = float(distance_str)
            time = float(time_str)
        except ValueError as exc:
            raise ValueError(
                f"مقدار فاصله/زمان نامعتبر در {edges_path} خط {line_number}: {line!r}"
            ) from exc

        graph.add_edge(
            source_id=source,
            destination_id=destination,
            distance=distance,
            time=time,
        )

    return graph