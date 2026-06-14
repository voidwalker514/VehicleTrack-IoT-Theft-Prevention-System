# ============================================================
# theft_detection.py — Theft & Anomaly Detection Engine
# IoT Vehicle Tracking & Theft Prevention System
# ============================================================
# PURPOSE : Analyses each GPS data point and returns an
#           AlertLevel + human-readable message using a set
#           of rule-based heuristics that mirror real industry
#           systems (fleet management, insurance telematics).
#
# Alert Levels:
#   SAFE     → Everything normal
#   WARNING  → Suspicious behaviour, monitor closely
#   CRITICAL → Likely theft or serious breach
# ============================================================

from datetime import datetime
from config import SPEED_THRESHOLD_KMPH, NIGHT_HOURS
from geofence import get_geofence_status


# ─── Alert Level Constants ─────────────────────────────────
ALERT_SAFE     = "SAFE"
ALERT_WARNING  = "WARNING"
ALERT_CRITICAL = "CRITICAL"


def _is_night_time(ts_str: str) -> bool:
    """Returns True if timestamp hour falls within configured night hours."""
    try:
        hour = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S").hour
        start_h, end_h = NIGHT_HOURS          # e.g., (22, 6)
        if start_h > end_h:                   # wraps midnight
            return hour >= start_h or hour < end_h
        return start_h <= hour < end_h
    except ValueError:
        return False


def analyse_point(gps_point: dict) -> dict:
    """
    Analyse a single GPS data point and return an alert dict.

    Args:
        gps_point (dict): Must contain keys:
            - timestamp  (str)  : "YYYY-MM-DD HH:MM:SS"
            - latitude   (float)
            - longitude  (float)
            - speed_kmph (float)
            - scenario   (str)  : scenario label from simulator

    Returns:
        dict with keys:
            - alert_level  : SAFE | WARNING | CRITICAL
            - alert_type   : short category string
            - alert_message: human-readable description
            - maps_url     : Google Maps deep link
    """
    lat        = gps_point["latitude"]
    lon        = gps_point["longitude"]
    speed      = gps_point["speed_kmph"]
    ts         = gps_point["timestamp"]
    scenario   = gps_point.get("scenario", "")

    geo_status = get_geofence_status(lat, lon)
    maps_url   = f"https://maps.google.com/?q={lat},{lon}"

    # ── Rule 1: Geofence breach ────────────────────────────
    if not geo_status["inside_geofence"]:
        dist_km = geo_status["distance_km"]
        return {
            "alert_level"  : ALERT_CRITICAL,
            "alert_type"   : "GEOFENCE_BREACH",
            "alert_message": (f"Vehicle has left the safe zone! "
                              f"Distance from centre: {dist_km} km. "
                              f"Location: {lat}, {lon}"),
            "maps_url"     : maps_url,
        }

    # ── Rule 2: Over-speed ────────────────────────────────
    if speed > SPEED_THRESHOLD_KMPH:
        return {
            "alert_level"  : ALERT_CRITICAL,
            "alert_type"   : "OVER_SPEED",
            "alert_message": (f"Vehicle speed ({speed} km/h) exceeds threshold "
                              f"({SPEED_THRESHOLD_KMPH} km/h). Possible theft!"),
            "maps_url"     : maps_url,
        }

    # ── Rule 3: Night-time movement ───────────────────────
    if _is_night_time(ts) and speed > 10:
        return {
            "alert_level"  : ALERT_WARNING,
            "alert_type"   : "NIGHT_MOVEMENT",
            "alert_message": (f"Vehicle moving at night ({ts}) at {speed} km/h. "
                              f"Verify with owner."),
            "maps_url"     : maps_url,
        }

    # ── Rule 4: Scenario-level theft flag (simulation only) ─
    if "Theft" in scenario or "stolen" in scenario.lower():
        return {
            "alert_level"  : ALERT_CRITICAL,
            "alert_type"   : "THEFT_DETECTED",
            "alert_message": (f"Theft scenario detected! Speed={speed} km/h. "
                              f"Location: {lat}, {lon}"),
            "maps_url"     : maps_url,
        }

    # ── Default: All clear ────────────────────────────────
    return {
        "alert_level"  : ALERT_SAFE,
        "alert_type"   : "ALL_CLEAR",
        "alert_message": f"Vehicle operating normally. Speed={speed} km/h.",
        "maps_url"     : maps_url,
    }


def classify_alerts(gps_data: list[dict]) -> list[dict]:
    """
    Run analyse_point() on a list of GPS points.
    Returns a merged list with original fields + alert fields.
    """
    enriched = []
    for point in gps_data:
        alert = analyse_point(point)
        enriched.append({**point, **alert})
    return enriched


# ─── Standalone test ───────────────────────────────────────
if __name__ == "__main__":
    sample = {
        "timestamp" : "2026-06-14 23:30:00",
        "latitude"  : 28.6139,
        "longitude" : 77.2090,
        "speed_kmph": 95.5,
        "scenario"  : "Theft Detected",
    }
    result = analyse_point(sample)
    for k, v in result.items():
        print(f"  {k:15s}: {v}")
