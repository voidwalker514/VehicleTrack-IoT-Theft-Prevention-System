# ============================================================
# geofence.py — Geofence Detection Engine
# IoT Vehicle Tracking & Theft Prevention System
# ============================================================
# PURPOSE : Determines whether a GPS coordinate is inside or
#           outside a defined circular safe zone (geofence).
#           Uses the Haversine formula for accurate distance
#           calculation on a sphere (Earth).
# ============================================================

import math
from config import GEOFENCE_CENTER_LAT, GEOFENCE_CENTER_LON, GEOFENCE_RADIUS_KM


def haversine_distance(lat1: float, lon1: float,
                       lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance (km) between two GPS coordinates
    using the Haversine formula.

    Args:
        lat1, lon1 : Source latitude and longitude (degrees)
        lat2, lon2 : Destination latitude and longitude (degrees)

    Returns:
        Distance in kilometres (float)
    """
    R = 6371.0  # Earth's mean radius in km

    # Convert degrees → radians
    phi1    = math.radians(lat1)
    phi2    = math.radians(lat2)
    d_phi   = math.radians(lat2 - lat1)
    d_lambda= math.radians(lon2 - lon1)

    # Haversine formula
    a = (math.sin(d_phi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 4)   # km, 4 decimal places ≈ 100 m precision


def is_inside_geofence(lat: float, lon: float) -> bool:
    """
    Returns True if (lat, lon) is within the configured geofence,
    False otherwise.
    """
    dist = haversine_distance(
        GEOFENCE_CENTER_LAT, GEOFENCE_CENTER_LON, lat, lon
    )
    return dist <= GEOFENCE_RADIUS_KM


def get_geofence_status(lat: float, lon: float) -> dict:
    """
    Returns a detailed status dict for a GPS point:
      - inside_geofence (bool)
      - distance_km     (float)
      - status_label    (str)
    """
    dist   = haversine_distance(GEOFENCE_CENTER_LAT, GEOFENCE_CENTER_LON, lat, lon)
    inside = dist <= GEOFENCE_RADIUS_KM
    return {
        "inside_geofence": inside,
        "distance_km"    : dist,
        "status_label"   : "INSIDE SAFE ZONE" if inside else "⚠️  OUTSIDE GEOFENCE",
    }


# ─── Standalone test ───────────────────────────────────────
if __name__ == "__main__":
    # Test with centre point (should be inside)
    test_cases = [
        (GEOFENCE_CENTER_LAT, GEOFENCE_CENTER_LON,       "Centre point"),
        (GEOFENCE_CENTER_LAT + 0.01, GEOFENCE_CENTER_LON,"Small offset"),
        (GEOFENCE_CENTER_LAT + 5.0,  GEOFENCE_CENTER_LON,"Far away"),
    ]
    for lat, lon, label in test_cases:
        result = get_geofence_status(lat, lon)
        print(f"{label:20s} → {result['status_label']}  ({result['distance_km']} km)")
