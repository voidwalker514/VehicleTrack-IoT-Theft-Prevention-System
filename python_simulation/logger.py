# ============================================================
# logger.py — CSV & Alert Logging Module
# IoT Vehicle Tracking & Theft Prevention System
# ============================================================
# PURPOSE : Persists all GPS readings and alert events to CSV
#           files in the data/ directory so they can later be
#           used for report generation and dashboard charts.
# ============================================================

import csv
import os
from datetime import datetime
from config import CSV_LOG_PATH, ALERT_LOG_PATH


# ─── CSV column headers ────────────────────────────────────
LOCATION_HEADERS = [
    "timestamp", "latitude", "longitude",
    "speed_kmph", "scenario", "step",
    "alert_level", "alert_type", "alert_message", "maps_url"
]

ALERT_HEADERS = [
    "timestamp", "alert_level", "alert_type",
    "alert_message", "latitude", "longitude", "maps_url"
]


def _ensure_dir(filepath: str) -> None:
    """Create parent directories if they do not exist."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)


def init_csv_files() -> None:
    """
    Create (or reset) the CSV log files with proper headers.
    Call this once at the start of each simulation run.
    """
    _ensure_dir(CSV_LOG_PATH)
    _ensure_dir(ALERT_LOG_PATH)

    with open(CSV_LOG_PATH,  "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=LOCATION_HEADERS).writeheader()

    with open(ALERT_LOG_PATH, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=ALERT_HEADERS).writeheader()

    print(f"[Logger] CSV files initialised:\n"
          f"         -> {CSV_LOG_PATH}\n"
          f"         -> {ALERT_LOG_PATH}")


def log_location(record: dict) -> None:
    """
    Append one enriched GPS record (with alert fields) to the
    location history CSV.

    Args:
        record (dict): Merged GPS + alert dict from classify_alerts()
    """
    _ensure_dir(CSV_LOG_PATH)
    row = {k: record.get(k, "") for k in LOCATION_HEADERS}
    with open(CSV_LOG_PATH, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=LOCATION_HEADERS).writerow(row)


def log_alert(record: dict) -> None:
    """
    Append one alert record to the alerts-only CSV (filtered for
    non-SAFE events only — keeps the alert log clean).

    Args:
        record (dict): Merged GPS + alert dict
    """
    if record.get("alert_level", "SAFE") == "SAFE":
        return   # don't clutter the alert log with normal events

    _ensure_dir(ALERT_LOG_PATH)
    row = {
        "timestamp"    : record.get("timestamp", ""),
        "alert_level"  : record.get("alert_level", ""),
        "alert_type"   : record.get("alert_type", ""),
        "alert_message": record.get("alert_message", ""),
        "latitude"     : record.get("latitude", ""),
        "longitude"    : record.get("longitude", ""),
        "maps_url"     : record.get("maps_url", ""),
    }
    with open(ALERT_LOG_PATH, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=ALERT_HEADERS).writerow(row)


def log_all(enriched_data: list[dict]) -> None:
    """
    Convenience function — logs every record in the list to both
    the location CSV and (conditionally) the alert CSV.

    Args:
        enriched_data: Output of theft_detection.classify_alerts()
    """
    for record in enriched_data:
        log_location(record)
        log_alert(record)
    print(f"[Logger] Logged {len(enriched_data)} records to {CSV_LOG_PATH}")
    alert_count = sum(1 for r in enriched_data if r.get("alert_level") != "SAFE")
    print(f"[Logger] {alert_count} alert event(s) written to {ALERT_LOG_PATH}")


# ─── Standalone test ───────────────────────────────────────
if __name__ == "__main__":
    init_csv_files()
    sample = {
        "timestamp"    : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "latitude"     : 28.6139,
        "longitude"    : 77.2090,
        "speed_kmph"   : 45.0,
        "scenario"     : "Normal Movement",
        "step"         : 1,
        "alert_level"  : "SAFE",
        "alert_type"   : "ALL_CLEAR",
        "alert_message": "Vehicle operating normally.",
        "maps_url"     : "https://maps.google.com/?q=28.6139,77.2090",
    }
    log_location(sample)
    print("Logger test passed.")
