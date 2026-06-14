# ============================================================
# alert_system.py — Alert Notification Engine
# IoT Vehicle Tracking & Theft Prevention System
# ============================================================
# PURPOSE : Centralises all alert output:
#             - Console print (always enabled)
#             - Email notification (optional, Gmail SMTP)
#             - ThingSpeak push (optional, cloud dashboard)
#
#           Each alert_level maps to a specific colour-coded
#           console output for easy visual scanning.
# ============================================================

import smtplib
import urllib.request
import urllib.parse
from email.mime.text       import MIMEText
from email.mime.multipart  import MIMEMultipart
from config import (
    EMAIL_SENDER, EMAIL_RECEIVER, EMAIL_PASSWORD,
    THINGSPEAK_WRITE_API_KEY, THINGSPEAK_BASE_URL
)

# ─── ANSI colour codes (work in most terminals) ────────────
COLOUR = {
    "RESET"   : "\033[0m",
    "GREEN"   : "\033[92m",
    "YELLOW"  : "\033[93m",
    "RED"     : "\033[91m",
    "CYAN"    : "\033[96m",
    "BOLD"    : "\033[1m",
}

LEVEL_COLOUR = {
    "SAFE"    : COLOUR["GREEN"],
    "WARNING" : COLOUR["YELLOW"],
    "CRITICAL": COLOUR["RED"],
}


def print_alert(record: dict) -> None:
    """
    Prints a colour-coded alert to the console.

    Args:
        record (dict): Enriched GPS + alert dict
    """
    level   = record.get("alert_level",   "SAFE")
    atype   = record.get("alert_type",    "ALL_CLEAR")
    message = record.get("alert_message", "")
    ts      = record.get("timestamp",     "")
    lat     = record.get("latitude",      0)
    lon     = record.get("longitude",     0)
    speed   = record.get("speed_kmph",    0)
    url     = record.get("maps_url",      "")

    col   = LEVEL_COLOUR.get(level, COLOUR["RESET"])
    reset = COLOUR["RESET"]
    bold  = COLOUR["BOLD"]

    # -- Header bar ---------------------------------------
    bar = "-" * 60
    print(f"\n{col}{bold}{bar}")
    print(f"  [{ts}]  {level}  |  {atype}")
    print(f"{bar}{reset}")
    print(f"  [Location] : {lat}, {lon}")
    print(f"  [Speed]    : {speed} km/h")
    print(f"  [Message]  : {message}")
    if level != "SAFE":
        print(f"  [Maps]     : {url}")
    print(f"{col}{bar}{reset}\n")


def send_email_alert(record: dict, enabled: bool = False) -> None:
    """
    Sends an email alert via Gmail SMTP.
    Set enabled=True and configure EMAIL_* in config.py.

    Args:
        record  (dict): Enriched GPS + alert dict
        enabled (bool): Feature flag — set True to activate
    """
    if not enabled:
        return
    if record.get("alert_level") == "SAFE":
        return

    subject = f"🚨 IoT Alert: {record.get('alert_type')} — Vehicle Tracker"
    body    = (
        f"Alert Level : {record['alert_level']}\n"
        f"Alert Type  : {record['alert_type']}\n"
        f"Timestamp   : {record['timestamp']}\n"
        f"Location    : {record['latitude']}, {record['longitude']}\n"
        f"Speed       : {record['speed_kmph']} km/h\n\n"
        f"Message     : {record['alert_message']}\n\n"
        f"Google Maps : {record['maps_url']}"
    )

    try:
        msg              = MIMEMultipart()
        msg["From"]      = EMAIL_SENDER
        msg["To"]        = EMAIL_RECEIVER
        msg["Subject"]   = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"[AlertSystem] ✅ Email sent to {EMAIL_RECEIVER}")

    except Exception as e:
        print(f"[AlertSystem] ❌ Email failed: {e}")


def push_to_thingspeak(record: dict, enabled: bool = False) -> None:
    """
    Pushes GPS data to ThingSpeak cloud dashboard.
    Set enabled=True once you have a real API key.

    ThingSpeak field mapping:
        field1 → Latitude
        field2 → Longitude
        field3 → Speed (km/h)
        field4 → Alert Level (0=SAFE, 1=WARNING, 2=CRITICAL)

    Args:
        record  (dict): Enriched GPS + alert dict
        enabled (bool): Feature flag
    """
    if not enabled:
        return

    level_map = {"SAFE": 0, "WARNING": 1, "CRITICAL": 2}
    params = {
        "api_key": THINGSPEAK_WRITE_API_KEY,
        "field1" : record.get("latitude",    0),
        "field2" : record.get("longitude",   0),
        "field3" : record.get("speed_kmph",  0),
        "field4" : level_map.get(record.get("alert_level", "SAFE"), 0),
    }

    try:
        url      = THINGSPEAK_BASE_URL + "?" + urllib.parse.urlencode(params)
        response = urllib.request.urlopen(url, timeout=5)
        code     = response.read().decode()
        if code != "0":
            print(f"[AlertSystem] ✅ ThingSpeak update #{code}")
        else:
            print("[AlertSystem] ⚠️  ThingSpeak returned 0 (check API key / rate limit)")
    except Exception as e:
        print(f"[AlertSystem] ❌ ThingSpeak push failed: {e}")


def process_alerts(enriched_data: list[dict],
                   email_enabled: bool      = False,
                   thingspeak_enabled: bool = False) -> None:
    """
    Run all alert channels for every record.

    Args:
        enriched_data       : List of enriched GPS+alert dicts
        email_enabled       : Activate email alerts (bool)
        thingspeak_enabled  : Activate ThingSpeak push (bool)
    """
    safe_count     = 0
    warning_count  = 0
    critical_count = 0

    for record in enriched_data:
        print_alert(record)
        send_email_alert(record, enabled=email_enabled)
        push_to_thingspeak(record, enabled=thingspeak_enabled)

        lvl = record.get("alert_level", "SAFE")
        if lvl == "SAFE"    : safe_count     += 1
        elif lvl == "WARNING": warning_count  += 1
        else                 : critical_count += 1

    print("\n" + "=" * 60)
    print(f"  ALERT SUMMARY")
    print(f"  SAFE     : {safe_count}")
    print(f"  WARNING  : {warning_count}")
    print(f"  CRITICAL : {critical_count}")
    print("=" * 60 + "\n")
