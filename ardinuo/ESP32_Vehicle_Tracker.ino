/*
 * ============================================================
 * ESP32_Vehicle_Tracker.ino
 * IoT Vehicle Tracking & Theft Prevention System
 * ============================================================
 * HARDWARE REQUIRED:
 *   - ESP32 Development Board (any variant)
 *   - NEO-6M or NEO-8M GPS Module (UART)
 *   - Active Buzzer (digital pin)
 *   - Red LED (theft alert)
 *   - Green LED (status OK)
 *
 * CONNECTIONS:
 *   GPS TX  → ESP32 GPIO 16 (RX2)
 *   GPS RX  → ESP32 GPIO 17 (TX2)
 *   GPS VCC → 3.3V
 *   GPS GND → GND
 *   Buzzer  → GPIO 25
 *   Red LED → GPIO 26 (via 330Ω resistor)
 *   Green LED → GPIO 27 (via 330Ω resistor)
 *
 * LIBRARIES NEEDED (install via Arduino Library Manager):
 *   - TinyGPSPlus  (by Mikal Hart)
 *   - HTTPClient   (built-in ESP32)
 *   - WiFi         (built-in ESP32)
 *
 * CLOUD: ThingSpeak (free account)
 *   Field 1 → Latitude
 *   Field 2 → Longitude
 *   Field 3 → Speed (km/h)
 *   Field 4 → Alert Level (0=Safe, 1=Warning, 2=Critical)
 * ============================================================
 */

#include <TinyGPSPlus.h>
#include <HardwareSerial.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <math.h>

// ─── WiFi Credentials ─────────────────────────────────────
const char* WIFI_SSID     = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// ─── ThingSpeak Settings ───────────────────────────────────
const char* TS_API_KEY  = "YOUR_THINGSPEAK_WRITE_API_KEY";
const char* TS_HOST     = "api.thingspeak.com";

// ─── Geofence Centre (degrees) ────────────────────────────
const double GEO_LAT    = 28.6139;   // New Delhi example
const double GEO_LON    = 77.2090;
const double GEO_RADIUS = 2.0;       // kilometres

// ─── Thresholds ───────────────────────────────────────────
const float SPEED_LIMIT = 80.0;      // km/h

// ─── Pin Definitions ──────────────────────────────────────
#define GPS_RX_PIN   16
#define GPS_TX_PIN   17
#define GPS_BAUD     9600
#define BUZZER_PIN   25
#define LED_RED      26
#define LED_GREEN    27

// ─── Objects ──────────────────────────────────────────────
TinyGPSPlus   gps;
HardwareSerial gpsSerial(2);   // UART2

// ─── Haversine Distance (km) ──────────────────────────────
double haversine(double lat1, double lon1, double lat2, double lon2) {
  const double R    = 6371.0;
  double dLat = radians(lat2 - lat1);
  double dLon = radians(lon2 - lon1);
  double a    = sin(dLat/2)*sin(dLat/2)
              + cos(radians(lat1))*cos(radians(lat2))
                *sin(dLon/2)*sin(dLon/2);
  return R * 2 * atan2(sqrt(a), sqrt(1-a));
}

// ─── Alert Levels ─────────────────────────────────────────
enum AlertLevel { SAFE = 0, WARNING = 1, CRITICAL = 2 };

AlertLevel evaluateAlert(double lat, double lon, float speedKmph) {
  double dist = haversine(GEO_LAT, GEO_LON, lat, lon);
  if (dist > GEO_RADIUS)      return CRITICAL;   // geofence breach
  if (speedKmph > SPEED_LIMIT) return CRITICAL;  // over-speed
  if (speedKmph > 60.0)        return WARNING;   // moderate warning
  return SAFE;
}

// ─── Output alert via LEDs + Buzzer ──────────────────────
void triggerAlert(AlertLevel level) {
  switch(level) {
    case CRITICAL:
      digitalWrite(LED_RED,   HIGH);
      digitalWrite(LED_GREEN, LOW);
      // Fast beep pattern: 3 short beeps
      for (int i = 0; i < 3; i++) {
        digitalWrite(BUZZER_PIN, HIGH); delay(200);
        digitalWrite(BUZZER_PIN, LOW);  delay(200);
      }
      break;
    case WARNING:
      digitalWrite(LED_RED,   HIGH);
      digitalWrite(LED_GREEN, HIGH);
      digitalWrite(BUZZER_PIN, HIGH); delay(500);
      digitalWrite(BUZZER_PIN, LOW);
      break;
    case SAFE:
      digitalWrite(LED_RED,   LOW);
      digitalWrite(LED_GREEN, HIGH);
      digitalWrite(BUZZER_PIN, LOW);
      break;
  }
}

// ─── Push data to ThingSpeak ──────────────────────────────
void pushToThingSpeak(double lat, double lon, float speed, int alertLevel) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WiFi] Not connected. Skipping push.");
    return;
  }

  HTTPClient http;
  String url = "http://api.thingspeak.com/update?api_key=";
  url += TS_API_KEY;
  url += "&field1=" + String(lat, 6);
  url += "&field2=" + String(lon, 6);
  url += "&field3=" + String(speed, 2);
  url += "&field4=" + String(alertLevel);

  http.begin(url);
  int code = http.GET();
  if (code > 0) {
    Serial.print("[ThingSpeak] Entry #: ");
    Serial.println(http.getString());
  } else {
    Serial.print("[ThingSpeak] Error: ");
    Serial.println(http.errorToString(code));
  }
  http.end();
}

// ─── Setup ────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  gpsSerial.begin(GPS_BAUD, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);

  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_RED,    OUTPUT);
  pinMode(LED_GREEN,  OUTPUT);

  // Startup indication
  digitalWrite(LED_GREEN, HIGH); delay(500);
  digitalWrite(LED_GREEN, LOW);

  // Connect WiFi
  Serial.print("[WiFi] Connecting to ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500); Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] Connected! IP: " + WiFi.localIP().toString());
    digitalWrite(LED_GREEN, HIGH);
  } else {
    Serial.println("\n[WiFi] Failed. Running offline.");
  }

  Serial.println("[System] IoT Vehicle Tracker Ready.");
}

// ─── Main Loop ────────────────────────────────────────────
unsigned long lastPush = 0;
const unsigned long PUSH_INTERVAL = 15000;   // 15 seconds (ThingSpeak limit)

void loop() {
  // Feed GPS serial data into TinyGPSPlus
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  // Act only when a new location fix is available
  if (gps.location.isUpdated()) {
    double lat      = gps.location.lat();
    double lon      = gps.location.lng();
    float  speedKmph = gps.speed.kmph();
    double distKm   = haversine(GEO_LAT, GEO_LON, lat, lon);

    AlertLevel alert = evaluateAlert(lat, lon, speedKmph);
    triggerAlert(alert);

    // ── Serial monitor output ──────────────────────────
    Serial.println("─────────────────────────────────────");
    Serial.print("[GPS] Lat: ");     Serial.println(lat,   6);
    Serial.print("[GPS] Lon: ");     Serial.println(lon,   6);
    Serial.print("[GPS] Speed: ");   Serial.print(speedKmph); Serial.println(" km/h");
    Serial.print("[GPS] Dist from centre: "); Serial.print(distKm); Serial.println(" km");
    Serial.print("[Alert] Level: ");
    if (alert == CRITICAL) Serial.println("CRITICAL ⚠️");
    else if (alert == WARNING) Serial.println("WARNING");
    else Serial.println("SAFE ✅");

    // ── Google Maps URL ───────────────────────────────
    Serial.print("[Maps] https://maps.google.com/?q=");
    Serial.print(lat, 6); Serial.print(","); Serial.println(lon, 6);

    // ── ThingSpeak push (rate-limited) ────────────────
    unsigned long now = millis();
    if (now - lastPush >= PUSH_INTERVAL) {
      pushToThingSpeak(lat, lon, speedKmph, (int)alert);
      lastPush = now;
    }
  }

  delay(100);  // Small yield to avoid WDT reset
}
