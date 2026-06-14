# ============================================================
# gps_simulator.py — Virtual GPS Coordinate Generator
# IoT Vehicle Tracking & Theft Prevention System
# ============================================================
# PURPOSE : Simulates GPS data so you can test without hardware.
#           Generates 4 realistic scenarios:
#             1. Normal movement  (within safe zone)
#             2. Parked vehicle   (stationary)
#             3. Theft scenario   (sudden high-speed movement)
#             4. Geofence breach  (exits safe zone)
# ============================================================

import random
import math
import time
from datetime import datetime
from config import (
    GEOFENCE_CENTER_LAT, GEOFENCE_CENTER_LON,
    GEOFENCE_RADIUS_KM, SCENARIOS
)


def _offset_coord(lat: float, lon: float, delta_lat: float, delta_lon: float):
    """Return a new (lat, lon) shifted by small degree deltas."""
    return round(lat + delta_lat, 6), round(lon + delta_lon, 6)


def simulate_normal_movement(steps: int = 20) -> list[dict]:
    """
    Simulates a vehicle driving normally inside the geofence.
    Speed stays below threshold. Location drifts slightly each step.
    """
    coords = []
    lat, lon = GEOFENCE_CENTER_LAT, GEOFENCE_CENTER_LON
    for step in range(steps):
        # Small random drift (≈ 100–300 m per step)
        delta_lat = random.uniform(-0.002, 0.002)
        delta_lon = random.uniform(-0.002, 0.002)
        lat, lon  = _offset_coord(lat, lon, delta_lat, delta_lon)
        speed_kmph = random.uniform(20, 60)
        coords.append({
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "latitude"  : lat,
            "longitude" : lon,
            "speed_kmph": round(speed_kmph, 2),
            "scenario"  : SCENARIOS["normal"],
            "step"      : step + 1,
        })
        time.sleep(0.05)   # tiny delay so timestamps differ in fast runs
    return coords


def simulate_parked(steps: int = 10) -> list[dict]:
    """
    Simulates a vehicle parked — nearly zero movement,
    very low speed (GPS jitter only).
    """
    coords = []
    lat = GEOFENCE_CENTER_LAT + 0.005
    lon = GEOFENCE_CENTER_LON + 0.005
    for step in range(steps):
        # Tiny GPS jitter (< 5 m)
        delta_lat = random.uniform(-0.00003, 0.00003)
        delta_lon = random.uniform(-0.00003, 0.00003)
        jitter_lat, jitter_lon = _offset_coord(lat, lon, delta_lat, delta_lon)
        coords.append({
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "latitude"  : jitter_lat,
            "longitude" : jitter_lon,
            "speed_kmph": round(random.uniform(0, 2), 2),
            "scenario"  : SCENARIOS["parked"],
            "step"      : step + 1,
        })
        time.sleep(0.05)
    return coords


def simulate_theft(steps: int = 15) -> list[dict]:
    """
    Simulates theft — vehicle suddenly moves at high speed
    in an unexpected direction.
    """
    coords = []
    lat = GEOFENCE_CENTER_LAT + 0.003
    lon = GEOFENCE_CENTER_LON + 0.003
    for step in range(steps):
        # Large jumps = high speed
        delta_lat = random.uniform(0.004, 0.008)   # always moving away
        delta_lon = random.uniform(0.004, 0.008)
        lat, lon  = _offset_coord(lat, lon, delta_lat, delta_lon)
        speed_kmph = random.uniform(90, 130)        # over threshold
        coords.append({
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "latitude"  : lat,
            "longitude" : lon,
            "speed_kmph": round(speed_kmph, 2),
            "scenario"  : SCENARIOS["stolen"],
            "step"      : step + 1,
        })
        time.sleep(0.05)
    return coords


def simulate_geofence_breach(steps: int = 15) -> list[dict]:
    """
    Simulates the vehicle gradually moving outside the geofence radius.
    """
    coords = []
    lat, lon = GEOFENCE_CENTER_LAT, GEOFENCE_CENTER_LON
    for step in range(steps):
        # Consistently move outward
        delta_lat = 0.006 * (step + 1)
        delta_lon = 0.006 * (step + 1)
        new_lat   = GEOFENCE_CENTER_LAT + delta_lat
        new_lon   = GEOFENCE_CENTER_LON + delta_lon
        speed_kmph = random.uniform(40, 70)
        coords.append({
            "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "latitude"  : round(new_lat, 6),
            "longitude" : round(new_lon, 6),
            "speed_kmph": round(speed_kmph, 2),
            "scenario"  : SCENARIOS["geofence"],
            "step"      : step + 1,
        })
        time.sleep(0.05)
    return coords


def get_full_simulation() -> list[dict]:
    """
    Combines all 4 scenarios into one continuous simulation dataset.
    Returns a flat list of GPS data points.
    """
    print("[GPS Simulator] Generating simulation data for all scenarios...")
    all_data = []
    all_data.extend(simulate_normal_movement(15))
    all_data.extend(simulate_parked(8))
    all_data.extend(simulate_theft(12))
    all_data.extend(simulate_geofence_breach(10))
    print(f"[GPS Simulator] Total GPS points generated: {len(all_data)}")
    return all_data


# ─── Standalone test ───────────────────────────────────────
if __name__ == "__main__":
    data = get_full_simulation()
    for point in data:
        print(point)
