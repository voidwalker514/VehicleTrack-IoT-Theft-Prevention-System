# ============================================================
# dashboard_visualizer.py — Terminal + Matplotlib Dashboard
# IoT Vehicle Tracking & Theft Prevention System
# ============================================================

import csv
import os


def _read_csv(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def print_dashboard_table(records: list[dict], last_n: int = 15) -> None:
    """Print the last N records as a formatted terminal table."""
    COLOUR_MAP = {"SAFE": "\033[92m", "WARNING": "\033[93m", "CRITICAL": "\033[91m"}
    RESET = "\033[0m"
    HEADER = "\033[1;94m"
    CYAN = "\033[96m"

    shown = records[-last_n:] if len(records) > last_n else records
    print(f"\n{HEADER}{'-'*110}\n{'LIVE DASHBOARD':^110}\n{'-'*110}{RESET}")
    header = f"{'#':>3}  {'Timestamp':19}  {'Lat':10}  {'Lon':10}  {'Speed':7}  {'Scenario':18}  {'Level':8}  Alert Type"
    print(CYAN + header + RESET)
    print("-" * 110)

    for i, r in enumerate(shown, 1):
        lvl  = r.get("alert_level", "SAFE")
        lcol = COLOUR_MAP.get(lvl, RESET)
        line = (f"{i:>3}  {r.get('timestamp',''):19}  "
                f"{r.get('latitude',''):10}  {r.get('longitude',''):10}  "
                f"{r.get('speed_kmph',''):7}  {r.get('scenario',''):18}  "
                f"{lcol}{lvl:8}{RESET}  {r.get('alert_type','')}")
        print(line)
    print("-" * 110 + "\n")


def generate_charts(records: list[dict]) -> None:
    """Generate and save matplotlib charts (speed, pie, GPS map)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("[Dashboard] Install matplotlib: pip install matplotlib")
        return

    os.makedirs("outputs", exist_ok=True)
    COLOUR_MAP = {"SAFE": "limegreen", "WARNING": "gold", "CRITICAL": "tomato"}

    steps  = list(range(1, len(records) + 1))
    speeds = [float(r.get("speed_kmph", 0)) for r in records]
    levels = [r.get("alert_level", "SAFE") for r in records]
    lats   = [float(r.get("latitude",  0)) for r in records]
    lons   = [float(r.get("longitude", 0)) for r in records]

    # 1. Speed chart
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(steps, speeds, color=[COLOUR_MAP.get(l, "grey") for l in levels], alpha=0.85)
    ax.axhline(y=80, color="red", linestyle="--", linewidth=1.2, label="Threshold 80 km/h")
    ax.set_title("Vehicle Speed Over Time", fontsize=14, fontweight="bold")
    ax.set_xlabel("GPS Ping #"); ax.set_ylabel("Speed (km/h)")
    ax.legend(); fig.tight_layout()
    fig.savefig("outputs/speed_chart.png", dpi=150); plt.close(fig)
    print("[Dashboard] Saved outputs/speed_chart.png")

    # 2. Alert pie chart
    from collections import Counter
    counts = Counter(levels)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(counts.values(), labels=counts.keys(),
           colors=[COLOUR_MAP.get(l, "grey") for l in counts.keys()],
           autopct="%1.1f%%", startangle=140)
    ax.set_title("Alert Level Distribution", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig("outputs/alert_pie.png", dpi=150); plt.close(fig)
    print("[Dashboard] Saved outputs/alert_pie.png")

    # 3. GPS path map
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(lons, lats, c=[COLOUR_MAP.get(l, "grey") for l in levels], s=40, alpha=0.75)
    ax.plot(lons, lats, "b--", linewidth=0.7, alpha=0.5)
    ax.scatter(lons[0], lats[0],   c="blue",  s=120, marker="^", label="Start")
    ax.scatter(lons[-1], lats[-1], c="black", s=120, marker="s", label="End")
    ax.set_title("GPS Vehicle Path", fontsize=14, fontweight="bold")
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    patches = [mpatches.Patch(color=v, label=k) for k, v in COLOUR_MAP.items()]
    ax.legend(handles=patches); ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    fig.savefig("outputs/gps_map.png", dpi=150); plt.close(fig)
    print("[Dashboard] Saved outputs/gps_map.png")


def run_dashboard(csv_path: str = "data/location_history.csv") -> None:
    records = _read_csv(csv_path)
    if not records:
        print("[Dashboard] No data. Run simulation first.")
        return
    print_dashboard_table(records)
    generate_charts(records)


if __name__ == "__main__":
    run_dashboard()
