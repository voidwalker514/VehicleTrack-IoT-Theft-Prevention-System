# IoT Vehicle Tracking & Theft Prevention System

[![IoT Course Project](https://img.shields.io/badge/IoT-Course%20Project-blue.svg)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build: ESP32 + Python](https://img.shields.io/badge/Stack-ESP32%20%7C%20Python%20%7C%20HTML-brightgreen.svg)](https://github.com/)

An industry-oriented Internet of Things (IoT) project designed for real-time tracking, geofence protection, and theft anomaly detection. This repository provides a complete implementation including **ESP32 firmware** for physical hardware deployment and a **high-fidelity Python Simulation** to validate tracking logic, generate reports (CSV/PDF), and visualize metrics without physical hardware.

---

## 1️⃣ Project Overview & System Architecture

### What is Vehicle Tracking?
Vehicle tracking uses global navigation satellite systems (such as GPS) combined with cellular, Wi-Fi, or LPWAN communication networks to track a vehicle's latitude, longitude, speed, and heading in real-time.

### What is Theft Prevention?
Theft prevention in modern IoT systems utilizes rule-based anomaly detection (e.g., geofencing, over-speed detection, night-time motion alerts) to detect unauthorized vehicle usage and automatically trigger alarms or remote ignition cuts (using relays).

### System Workflow
```
[ GPS Satellite ]
       │ (NMEA Data)
       ▼
 ┌───────────┐      (WiFi / Serial)      ┌────────────────────┐
 │   ESP32   │ ────────────────────────> │  ThingSpeak Cloud  │
 └─────┬─────┘                           └─────────┬──────────┘
       │                                           │
       ├─► [ Buzzer Alert ]                        ▼
       ├─► [ Active Relay ]              ┌────────────────────┐
       └─► [ Status LEDs ]               │  HTML5 Dashboard   │
                                         └────────────────────┘
 ┌────────────────────────────────────────────────────────────┐
 │                     PYTHON VIRTUAL SIMULATOR                │
 │  [gps_simulator] ──► [theft_detection] ──► [logger/reports]│
 └────────────────────────────────────────────────────────────┘
```

---

## 2️⃣ Repository Folder Structure

```
IoT-Vehicle-Tracking-Theft-Prevention-System/
│
├── arduino_code/
│   └── ESP32_Vehicle_Tracker/
│       └── ESP32_Vehicle_Tracker.ino   # ESP32 C++ firmware with WiFi & TinyGPS++
│
├── python_simulation/
│   ├── __init__.py
│   ├── config.py                       # Threshold values, coordinates & paths
│   ├── gps_simulator.py                # Simulated movements (normal, theft, breach)
│   ├── geofence.py                     # Haversine distance geofence checker
│   ├── theft_detection.py              # Rule-based threat & speed evaluation
│   ├── logger.py                       # CSV data formatting and file writer
│   ├── alert_system.py                 # Terminal logs, email alerts, ThingSpeak push
│   ├── dashboard_visualizer.py         # Matplotlib chart generator (PNG outputs)
│   └── report_generator.py             # fpdf2 PDF report builder
│
├── dashboard/
│   └── index.html                      # Premium dark-mode HTML simulation web interface
│
├── circuit_diagram/
│   └── circuit_connections.txt         # ASCII circuit diagram & connection pin table
│
├── data/
│   ├── location_history.csv            # Auto-generated GPS location logs (created at runtime)
│   └── alerts.csv                      # Auto-generated anomaly event logs (created at runtime)
│
├── outputs/
│   ├── speed_chart.png                 # Auto-generated matplotlib speed telemetry
│   ├── alert_pie.png                   # Auto-generated alert level split
│   └── gps_map.png                     # Auto-generated spatial coordinates path map
│
├── reports/
│   └── location_report.pdf             # Professional PDF execution summary
│
├── requirements.txt                    # Python library requirements
└── main.py                             # Simulation command-line orchestrator
```

---

## 3️⃣ Hardware Setup & Connections

The hardware system utilizes the **ESP32 microcontroller** for processing, the **NEO-6M GPS module** for coordinate telemetry, a **buzzer** for audible local alarms, and **status LEDs**.

Refer to [circuit_connections.txt](circuit_diagram/circuit_connections.txt) for detailed connection mappings. Below is the pin connection quick-sheet:

| Component Pin | ESP32 GPIO Connection | Description |
| :--- | :--- | :--- |
| **GPS VCC** | `3.3V` | 3.3V Power Supply |
| **GPS GND** | `GND` | Common Ground |
| **GPS TX** | `GPIO 16 (RX2)` | Serial communication receive |
| **GPS RX** | `GPIO 17 (TX2)` | Serial communication transmit |
| **Buzzer (+)** | `GPIO 25` | Local alarm output |
| **Red LED (Anode)** | `GPIO 26` | Theft / Alert Status indicator |
| **Green LED (Anode)**| `GPIO 27` | Heartbeat / Safe status indicator |

*Note: Use a 330Ω resistor in series with the Anode (+) of the Red and Green LEDs to restrict current flow and protect the ESP32 GPIO pins.*

---

## 4️⃣ Software Setup & Execution

### Option A: Local Virtual Python Simulation (No Hardware Needed)
Use the simulator to run realistic GPS scenarios, log positions, create reports, and compile analytical telemetry charts.

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/IoT-Vehicle-Tracking-Theft-Prevention-System.git
   cd IoT-Vehicle-Tracking-Theft-Prevention-System
   ```
2. **Install Dependencies:**
   Ensure Python 3.8+ is installed.
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the Simulation:**
   Run the full pipeline using the orchestrator:
   ```bash
   python main.py
   ```
   To run specific scenarios, use configuration arguments:
   ```bash
   # Options for --scenario: all, normal, parked, theft, geofence
   python main.py --scenario theft --steps 20
   ```

### Option B: HTML5 Interactive Web Dashboard
An interactive frontend simulation is provided to showcase the project in a web browser.
1. Open the [dashboard/index.html](dashboard/index.html) file directly in any modern browser.
2. Select simulation scenarios using the interactive action buttons (`Normal Drive`, `Parked`, `Theft`, `Geofence Breach`).
3. View real-time speedometers, live coordinates, Google Maps links, and active alert notifications instantly.

### Option C: Physical ESP32 Hardware Deployment
1. Install the Arduino IDE.
2. Install the **ESP32 Board Package** in Arduino IDE (Tools > Board > Boards Manager).
3. Search for and install the **TinyGPSPlus** library in the Library Manager.
4. Open [ESP32_Vehicle_Tracker.ino](arduino_code/ESP32_Vehicle_Tracker/ESP32_Vehicle_Tracker.ino).
5. Update `WIFI_SSID`, `WIFI_PASSWORD`, and `TS_API_KEY` (ThingSpeak Write Key) with your credentials.
6. Connect the ESP32 to your PC, choose your board port, and click **Upload**.

---

## 5️⃣ Cloud Dashboard Integration (ThingSpeak)

To stream your live coordinates to a public cloud channel:
1. Create a free account at [ThingSpeak](https://thingspeak.com/).
2. Create a **New Channel** called "Vehicle Tracker".
3. Configure the following 4 Fields:
   - **Field 1:** Latitude
   - **Field 2:** Longitude
   - **Field 3:** Speed (km/h)
   - **Field 4:** Alert Level (0 = Safe, 1 = Warning, 2 = Critical)
4. Copy the **Write API Key** from the "API Keys" tab.
5. Paste it in `python_simulation/config.py` (for the python simulator) or in your Arduino script.

---

## 6️⃣ Sample Analytical Outputs

Once you execute the simulation pipeline (`python main.py`), the system creates logs in the `data/` folder and generates visualization analytics in the `outputs/` folder:

- **GPS Map Route (`outputs/gps_map.png`):** Shows the path taken by the vehicle with colour-coded status zones.
- **Speed Profile (`outputs/speed_chart.png`):** Displays speed telemetry mapped against safe thresholds.
- **Alert Pie Chart (`outputs/alert_pie.png`):** Illustrates the breakdown of safe vs. critical states during execution.
- **PDF Report (`reports/location_report.pdf`):** A professional system summary showing a structured telemetry log, alert frequencies, and metadata.

---

## 7️⃣ Future Enhancements
- **Cellular Failover:** Integrate a SIM900A/SIM800L GSM/GPRS module to send SMS notifications when WiFi is unavailable.
- **Ignition Lock Relay:** Add an active relay mechanism to allow remote vehicle shutdown from the dashboard.
- **OBD-II Telemetry:** Read engine parameters directly using the OBD-II protocol.
- **Mobile Application:** Build a Flutter or React Native mobile interface with Google Maps SDK integration.
