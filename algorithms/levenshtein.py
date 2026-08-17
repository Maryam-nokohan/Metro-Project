from typing import List, Tuple


def levenshtein_distance(a: str, b: str) -> int:

    len_a, len_b = len(a), len(b)

    if len_a == 0:
        return len_b
    if len_b == 0:
        return len_a

    dp = [[0] * (len_b + 1) for _ in range(len_a + 1)]

    for i in range(len_a + 1):
        dp[i][0] = i
    for j in range(len_b + 1):
        dp[0][j] = j

    for i in range(1, len_a + 1):
        for j in range(1, len_b + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost,
            )

    return dp[len_a][len_b]


def find_closest_station(
    query: str, station_names: List[str], max_results: int = 3
) -> List[Tuple[str, int]]:

    scored = [(name, levenshtein_distance(query, name)) for name in station_names]
    scored.sort(key=lambda pair: pair[1])
    return scored[:max_results]
