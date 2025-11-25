"""Constants for the Hargassner Integration."""
from typing import Final

# Integration domain
DOMAIN: Final = "bauergroup_hargassnerintegration"

# Configuration keys
CONF_FIRMWARE: Final = "firmware"
CONF_DEVICE_NAME: Final = "device_name"
CONF_LANGUAGE: Final = "language"
CONF_SENSOR_SET: Final = "sensor_set"
CONF_PELLET_ENERGY: Final = "pellet_energy_kwh_per_kg"
CONF_EFFICIENCY: Final = "efficiency_percent"

# Language options
LANGUAGE_EN: Final = "EN"
LANGUAGE_DE: Final = "DE"

# Sensor set options
SENSOR_SET_STANDARD: Final = "STANDARD"
SENSOR_SET_FULL: Final = "FULL"

# Telnet settings
TELNET_PORT: Final = 23
TELNET_TIMEOUT: Final = 10.0
TELNET_RECONNECT_DELAY: Final = 5.0
TELNET_MAX_RECONNECT_DELAY: Final = 300.0
TELNET_BUFFER_SIZE: Final = 65536

# Update intervals
UPDATE_INTERVAL: Final = 5  # seconds

# Connection states
STATE_CONNECTED: Final = "connected"
STATE_DISCONNECTED: Final = "disconnected"
STATE_CONNECTING: Final = "connecting"

# Boiler states (ZK parameter)
BOILER_STATES_EN: Final = [
    "Unknown",
    "Off",
    "Preparing start",
    "Boiler start",
    "Monitoring ignition",
    "Ignition",
    "Transition to FF",
    "Full firing",
    "Ember preservation",
    "Waiting for AR",
    "Ash removal",
    "-",
    "Cleaning",
]

BOILER_STATES_DE: Final = [
    "Unbekannt",
    "Aus",
    "Startvorbereitung",
    "Kessel Start",
    "Zündüberwachung",
    "Zündung",
    "Übergang LB",
    "Leistungsbrand",
    "Gluterhaltung",
    "Warten auf EA",
    "Entaschung",
    "-",
    "Putzen",
]

# Error codes
ERROR_CODES: Final = {
    "5": {"en": "Empty ash drawer", "de": "Aschelade entleeren"},
    "6": {"en": "Ash drawer too full", "de": "Aschelade zu voll"},
    "29": {"en": "Combustion fault", "de": "Verbrennungsstörung"},
    "30": {"en": "Battery empty", "de": "Batterie leer"},
    "31": {"en": "Feed motor blocked", "de": "Blockade Einschubmotor"},
    "32": {"en": "Fill time exceeded", "de": "Füllzeit überschritten"},
    "70": {"en": "Pellet stock low", "de": "Pelletslagerstand niedrig"},
    "89": {"en": "Grate stiff", "de": "Schieberost schwergängig"},
    "93": {"en": "Ash drawer open", "de": "Aschelade offen"},
    "155": {"en": "Cleaning defective", "de": "Spülung defekt"},
    "227": {"en": "Storage room switch off", "de": "Lagerraumschalter aus"},
    "228": {"en": "Pellet container almost empty", "de": "Pelletsbehälter fast leer"},
    "229": {"en": "Check level indicator", "de": "Füllstandsmelder kontrollieren"},
    "371": {"en": "Check combustion chamber", "de": "Brennraum prüfen"},
}

# Firmware versions
# IMPORTANT: Keep this list in sync with FIRMWARE_TEMPLATES in src/firmware_templates.py
# When adding a new firmware version:
# 1. Add the XML template to FIRMWARE_TEMPLATES in src/firmware_templates.py
# 2. Add the version string here
# 3. Run tools/parameter_validator.py to verify consistency
FIRMWARE_VERSIONS: Final = [
    "V14_1HAR_q1",
    "V14_0HAR_q",
]

# Energy calculation defaults
DEFAULT_PELLET_ENERGY: Final = 4.8  # kWh per kg (Heizwert)
DEFAULT_EFFICIENCY: Final = 90  # % Wirkungsgrad
