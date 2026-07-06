// --------------------
// CONTROLLER.INO -- Single Sensor Ver
// VERSION 0.4
// --------------------

#include <OneWire.h>
#include <DallasTemperature.h>
#include <avr/wdt.h>
#include <EEPROM.h>

#define ONE_WIRE_PIN 2
#define MOSFET_PIN 0

// --------------------
// SENSOR SETUP
// --------------------
OneWire oneWire(ONE_WIRE_PIN);
DallasTemperature sensors(&oneWire);

// --------------------
// THRESHOLDS
// --------------------
const float ON_TEMP  = 0.0;
const float OFF_TEMP = 10.0;

// --------------------
// VALIDATION RULES
// --------------------
const int REQUIRED_STARTUP_GOOD = 10;
const int BAD_LATCH_LIMIT = 3;

const float MIN_VALID_TEMP = -40;
const float MAX_VALID_TEMP = 80;

// --------------------
// EEPROM FAULT FLAG
// --------------------
const int EEPROM_FAULT_ADDR = 0;

// --------------------
// STATE MACHINE
// --------------------
enum BootState {
  STARTUP,
  RUN,
  FAILSAFE
};

BootState state = STARTUP;

bool heaterOn = false;

// startup tracking
int goodStreak = 0;

// runtime fault tracking
int badCount = 0;
int globalFailureCount = 0;

// --------------------
// SENSOR VALIDATION
// --------------------
bool isValid(float t) {
  if (t == DEVICE_DISCONNECTED_C) return false;
  if (t < MIN_VALID_TEMP || t > MAX_VALID_TEMP) return false;
  return true;
}

// --------------------
// PERMANENT FAULT CHECK
// --------------------
bool isLatchedFault() {
  return EEPROM.read(EEPROM_FAULT_ADDR) == 1;
}

void latchFault() {
  EEPROM.write(EEPROM_FAULT_ADDR, 1);
}

// --------------------
// SAFETY SHUTDOWN
// --------------------
void shutdownSystem() {
  digitalWrite(MOSFET_PIN, LOW);
  heaterOn = false;

  state = FAILSAFE;

  globalFailureCount++;

  if (globalFailureCount >= 3) {
    latchFault(); // permanent lockout
  }
}

// --------------------
// SETUP
// --------------------
void setup() {

  pinMode(MOSFET_PIN, OUTPUT);
  digitalWrite(MOSFET_PIN, LOW); // FORCE OFF IMMEDIATELY

  wdt_enable(WDTO_4S);
  wdt_reset();

  sensors.begin();

  delay(1000);
  wdt_reset();

  // if permanently faulted, skip everything
  if (isLatchedFault()) {
    state = FAILSAFE;
  }
}

// --------------------
// MAIN LOOP
// --------------------
void loop() {

  wdt_reset();

  // HARD SAFETY: always enforce OFF at loop entry
  digitalWrite(MOSFET_PIN, LOW);

  sensors.requestTemperatures();
  float temp = sensors.getTempCByIndex(0);

  wdt_reset();

  unsigned long now = millis();

  // =====================================================
  // PERMANENT FAILSAFE (latched in EEPROM)
  // =====================================================
  if (isLatchedFault()) {
    state = FAILSAFE;
  }

  if (state == FAILSAFE) {
    heaterOn = false;
    delay(1000);
    return;
  }

  // =====================================================
  // STARTUP PHASE (sensor arming)
  // =====================================================
  if (state == STARTUP) {

    if (isValid(temp)) {
      goodStreak++;
    } else {
      goodStreak = 0;
    }

    if (goodStreak >= REQUIRED_STARTUP_GOOD) {
      state = RUN;
      badCount = 0;
    }

    delay(500);
    return;
  }

  // =====================================================
  // RUN PHASE (fault detection)
  // =====================================================
  if (!isValid(temp)) {

    badCount++;

    if (badCount >= BAD_LATCH_LIMIT) {
      shutdownSystem();
      delay(1000);
      return;
    }

  } else {
    if (badCount > 0 && (millis() - now > 10000)) {
      badCount = 0;
    }
  }

  // =====================================================
  // THERMOSTAT CONTROL
  // =====================================================
  if (!heaterOn && temp <= ON_TEMP) {
    heaterOn = true;
    digitalWrite(MOSFET_PIN, HIGH);
  }

  if (heaterOn && temp >= OFF_TEMP) {
    heaterOn = false;
    digitalWrite(MOSFET_PIN, LOW);
  }

  delay(1000);
}