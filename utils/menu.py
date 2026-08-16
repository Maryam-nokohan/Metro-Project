from typing import List, Optional

from models.graph import Graph


def print_header(title: str) -> None:
    print("\n" + "=" * 62)
    print(title.center(62))
    print("=" * 62)


def print_menu(title: str, options: List[str]) -> None:
    print_header(title)
    for i, option in enumerate(options, start=1):
        print(f"  {i}) {option}")
    print("  0) بازگشت")


def prompt_choice(max_option: int) -> int:

    while True:
        raw = input("\nانتخاب شما: ").strip()
        if raw.isdigit() and 0 <= int(raw) <= max_option:
            return int(raw)
        print(f"❌ لطفاً عددی بین 0 تا {max_option} وارد کنید.")


def choose_station(
    graph: Graph, prompt: str = "یک ایستگاه انتخاب کنید"
) -> Optional[str]:

    station_ids = graph.station_ids()
    print(f"\n{prompt} (برای انصراف 0 را بزنید):")
    for i, station_id in enumerate(station_ids, start=1):
        print(f"  {i:2}) {station_id}")

    while True:
        raw = input("شماره‌ی ایستگاه: ").strip()
        if raw == "0":
            return None
        if raw.isdigit() and 1 <= int(raw) <= len(station_ids):
            return station_ids[int(raw) - 1]
        print(f"❌ لطفاً عددی بین 0 تا {len(station_ids)} وارد کنید.")


def prompt_criterion() -> str:
    print("\nمعیار مسیر را انتخاب کنید:")
    print("  1) فاصله (کیلومتر)")
    print("  2) زمان (دقیقه)")
    choice = prompt_choice(2)
    return "time" if choice == 2 else "distance"


def prompt_float(prompt: str, default: Optional[float] = None) -> float:
    suffix = f" [پیش‌فرض={default}]" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if not raw and default is not None:
            return default
        try:
            return float(raw)
        except ValueError:
            print("❌ لطفاً یک عدد معتبر وارد کنید.")


def prompt_int(prompt: str, default: Optional[int] = None) -> int:
    suffix = f" [پیش‌فرض={default}]" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if not raw and default is not None:
            return default
        try:
            return int(raw)
        except ValueError:
            print("❌ لطفاً یک عدد صحیح معتبر وارد کنید.")


def prompt_text(prompt: str) -> str:
    return input(f"{prompt}: ").strip()


def pause() -> None:
    input("\n(برای بازگشت به منو، Enter را بزنید...) ")
