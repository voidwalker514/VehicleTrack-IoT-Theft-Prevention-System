# ============================================================
# config.py — Project Configuration
# IoT Vehicle Tracking & Theft Prevention System
# ============================================================
# Author : Your Name
# Course  : IoT Systems Engineering
# ============================================================

# ─── Geofence Settings ─────────────────────────────────────
# Define the "safe zone" center and radius
GEOFENCE_CENTER_LAT  = 28.6139    # Latitude  (e.g., New Delhi)
GEOFENCE_CENTER_LON  = 77.2090    # Longitude (e.g., New Delhi)
GEOFENCE_RADIUS_KM   = 2.0        # Allowed radius in kilometres

# ─── Theft Detection Settings ──────────────────────────────
SPEED_THRESHOLD_KMPH = 80         # Warn if speed exceeds this
MAX_IDLE_MINUTES     = 30         # Warn if parked > this (minutes)
NIGHT_HOURS          = (22, 6)    # Movement between 22:00–06:00 triggers alert

# ─── Simulation Settings ───────────────────────────────────
SIMULATION_INTERVAL_SEC = 2       # Seconds between each simulated GPS ping
TOTAL_SIMULATION_STEPS  = 60      # Number of GPS pings to simulate

# ─── File Paths ────────────────────────────────────────────
CSV_LOG_PATH    = "data/location_history.csv"
ALERT_LOG_PATH  = "data/alerts.csv"
PDF_REPORT_PATH = "reports/location_report.pdf"

# ─── ThingSpeak (Cloud Dashboard) ──────────────────────────
# Replace with your real ThingSpeak Write API Key when available
THINGSPEAK_WRITE_API_KEY = "YOUR_THINGSPEAK_WRITE_API_KEY"
THINGSPEAK_CHANNEL_ID    = "YOUR_CHANNEL_ID"
THINGSPEAK_BASE_URL      = "https://api.thingspeak.com/update"

# ─── Email Alert Settings (Optional) ───────────────────────
EMAIL_SENDER   = "your_email@gmail.com"
EMAIL_RECEIVER = "receiver_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"       # Use Gmail App Password

# ─── Google Maps URL Template ──────────────────────────────
GOOGLE_MAPS_TEMPLATE = "https://maps.google.com/?q={lat},{lon}"

# ─── Simulation Scenario Labels ────────────────────────────
SCENARIOS = {
    "normal"  : "Normal Movement",
    "parked"  : "Vehicle Parked",
    "stolen"  : "Theft Detected",
    "geofence": "Geofence Breach",
}
