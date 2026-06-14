"""
main.py — Master Entry Point
IoT Vehicle Tracking & Theft Prevention System
==============================================
Run this file to execute the complete simulation pipeline:

  python main.py [--scenario all|normal|parked|theft|geofence]
                 [--steps N]
                 [--no-charts]
                 [--no-pdf]
                 [--email]
                 [--thingspeak]

Examples:
  python main.py
  python main.py --scenario theft --steps 20
  python main.py --no-charts --no-pdf
"""

import argparse
import sys
import os

# ── Ensure python_simulation/ is on the path ──────────────
SIM_DIR = os.path.join(os.path.dirname(__file__), "python_simulation")
if SIM_DIR not in sys.path:
    sys.path.insert(0, SIM_DIR)

from python_simulation.gps_simulator      import (
    simulate_normal_movement, simulate_parked,
    simulate_theft, simulate_geofence_breach,
    get_full_simulation
)
from python_simulation.theft_detection    import classify_alerts
from python_simulation.logger             import init_csv_files, log_all
from python_simulation.alert_system       import process_alerts
from python_simulation.dashboard_visualizer import run_dashboard
from python_simulation.report_generator  import generate_all_reports

BANNER = r"""
  ___     _____   __   __        _      _      _
 |_ _|___| __\ \ / /  / /___ _ _| |_ __| | ___( )___
  | |/ _ \  _|\ V /  / // -_) ' \  _/ _` |(_-<|/(_-<
 |___\___/_|   \_/  /_/ \___|_||_\__\__,_|/__/  /__/

 IoT Vehicle Tracking & Theft Prevention System
 ==============================================
 Author  : IoT Engineering Student
 Purpose : Simulate GPS tracking, geofencing, theft alerts
"""


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="IoT Vehicle Tracking Simulation"
    )
    parser.add_argument(
        "--scenario",
        choices=["all", "normal", "parked", "theft", "geofence"],
        default="all",
        help="Simulation scenario to run (default: all)"
    )
    parser.add_argument(
        "--steps", type=int, default=None,
        help="Number of GPS pings per scenario"
    )
    parser.add_argument("--no-charts",    action="store_true", help="Skip chart generation")
    parser.add_argument("--no-pdf",       action="store_true", help="Skip PDF report")
    parser.add_argument("--email",        action="store_true", help="Enable email alerts (configure config.py)")
    parser.add_argument("--thingspeak",   action="store_true", help="Enable ThingSpeak push (configure config.py)")
    return parser.parse_args()


def run_scenario(scenario: str, steps: int) -> list[dict]:
    """Select and run the appropriate GPS simulator."""
    n = steps or 20
    if   scenario == "normal"  : return simulate_normal_movement(n)
    elif scenario == "parked"  : return simulate_parked(n)
    elif scenario == "theft"   : return simulate_theft(n)
    elif scenario == "geofence": return simulate_geofence_breach(n)
    else                       : return get_full_simulation()   # all


def main() -> None:
    print(BANNER)
    args = build_args()

    # ── Phase 1: Generate GPS data ─────────────────────────
    print(f"[Main] Scenario : {args.scenario.upper()}")
    gps_data = run_scenario(args.scenario, args.steps)
    print(f"[Main] GPS points generated: {len(gps_data)}")

    # ── Phase 2: Theft & geofence analysis ─────────────────
    print("[Main] Running theft/geofence detection...")
    enriched = classify_alerts(gps_data)

    # ── Phase 3: Log to CSV ────────────────────────────────
    print("[Main] Logging data to CSV...")
    init_csv_files()
    log_all(enriched)

    # ── Phase 4: Console alerts ────────────────────────────
    print("[Main] Processing alerts...")
    process_alerts(
        enriched,
        email_enabled=args.email,
        thingspeak_enabled=args.thingspeak
    )

    # ── Phase 5: Dashboard & charts ────────────────────────
    if not args.no_charts:
        print("[Main] Generating dashboard...")
        run_dashboard()
    else:
        print("[Main] Chart generation skipped (--no-charts).")

    # ── Phase 6: PDF report ────────────────────────────────
    if not args.no_pdf:
        print("[Main] Generating reports...")
        generate_all_reports()
    else:
        print("[Main] PDF generation skipped (--no-pdf).")

    print("\n[Main] SUCCESS: Simulation complete!")
    print("[Main] Check the following folders for outputs:")
    print("       data/        -> CSV logs")
    print("       outputs/     -> Charts (PNG)")
    print("       reports/     -> PDF & summary CSV")


if __name__ == "__main__":
    main()
