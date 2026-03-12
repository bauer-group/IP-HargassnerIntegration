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
TELNET_BUFFER_SIZE: Final = 65536
TELNET_DATA_STALENESS_TIMEOUT: Final = 60.0  # Reconnect if no data for this many seconds

# Update intervals (legacy - now using push-based updates)
# UPDATE_INTERVAL: Final = 5  # seconds - no longer used

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

# Error codes (source: Hargassner Nano-PK 6-32 Manual, shb-nano-pk-6-32-de.pdf)
ERROR_CODES: Final = {
    # Kessel & Sicherheit (1-9)
    "1": {"en": "Overtemperature - STB triggered", "de": "Übertemperatur STB gefallen"},
    "2": {"en": "Overcurrent feed screw", "de": "Überstrom Einschubschnecke"},
    "3": {"en": "Overcurrent room auger 1", "de": "Überstrom Raumaustragungsschnecke 1"},
    "4": {"en": "Thermal protection room auger 1", "de": "Thermoschutz Raumaustragungsschnecke 1"},
    "5": {"en": "Empty ash drawer", "de": "Aschelade entleeren"},
    "6": {"en": "Ash drawer too full", "de": "Aschelade zu voll"},
    "7": {"en": "Grate does not open", "de": "Schieberost öffnet nicht"},
    "8": {"en": "Grate does not close", "de": "Schieberost schließt nicht"},
    "9": {"en": "Overcurrent cleaning device", "de": "Überstrom Putzeinrichtung"},
    # Fühler & Sensoren (10-59)
    "10": {"en": "Flue gas sensor wrong connection", "de": "Rauchgasfühler falsch angeschlossen"},
    "11": {"en": "Flue gas sensor disconnected", "de": "Rauchgasfühler Unterbrechung"},
    "12": {"en": "Boiler sensor short circuit", "de": "Kesselfühler Kurzschluss"},
    "13": {"en": "Boiler sensor disconnected", "de": "Kesselfühler Unterbrechung"},
    "14": {"en": "DHW sensor 1 short circuit", "de": "Boilerfühler 1 Kurzschluss"},
    "15": {"en": "DHW sensor 1 disconnected", "de": "Boilerfühler 1 Unterbrechung"},
    "16": {"en": "Outdoor sensor short circuit", "de": "Außenfühler Kurzschluss"},
    "17": {"en": "Outdoor sensor disconnected", "de": "Außenfühler Unterbrechung"},
    "18": {"en": "Flow sensor HC1 short circuit", "de": "Vorlauffühler HK1 Kurzschluss"},
    "19": {"en": "Flow sensor HC1 disconnected", "de": "Vorlauffühler HK1 Unterbrechung"},
    "20": {"en": "Flow sensor HC2 short circuit", "de": "Vorlauffühler HK2 Kurzschluss"},
    "21": {"en": "Flow sensor HC2 disconnected", "de": "Vorlauffühler HK2 Unterbrechung"},
    "22": {"en": "Room sensor HC1 short circuit", "de": "Raumfühler HK1 Kurzschluss"},
    "23": {"en": "Room sensor HC1 disconnected", "de": "Raumfühler HK1 Unterbrechung"},
    "24": {"en": "Room sensor HC2 short circuit", "de": "Raumfühler HK2 Kurzschluss"},
    "25": {"en": "Room sensor HC2 disconnected", "de": "Raumfühler HK2 Unterbrechung"},
    "34": {"en": "Buffer sensor top short circuit", "de": "Pufferfühler oben Kurzschluss"},
    "35": {"en": "Buffer sensor top disconnected", "de": "Pufferfühler oben Unterbrechung"},
    "36": {"en": "Buffer sensor bottom short circuit", "de": "Pufferfühler unten Kurzschluss"},
    "37": {"en": "Buffer sensor bottom disconnected", "de": "Pufferfühler unten Unterbrechung"},
    "39": {"en": "DHW sensor 2 short circuit", "de": "Boilerfühler 2 Kurzschluss"},
    "40": {"en": "DHW sensor 2 disconnected", "de": "Boilerfühler 2 Unterbrechung"},
    "46": {"en": "Return sensor short circuit", "de": "Rücklauffühler Kurzschluss"},
    "47": {"en": "Return sensor disconnected", "de": "Rücklauffühler Unterbrechung"},
    "52": {"en": "External heat sensor short circuit", "de": "Fremdwärmefühler Kurzschluss"},
    "53": {"en": "External heat sensor disconnected", "de": "Fremdwärmefühler Unterbrechung"},
    "54": {"en": "Buffer sensor middle short circuit", "de": "Pufferfühler Mitte Kurzschluss"},
    "55": {"en": "Buffer sensor middle disconnected", "de": "Pufferfühler Mitte Unterbrechung"},
    "56": {"en": "Buffer sensor upper middle short circuit", "de": "Pufferfühler oben Mitte Kurzschluss"},
    "57": {"en": "Buffer sensor upper middle disconnected", "de": "Pufferfühler oben Mitte Unterbrechung"},
    "58": {"en": "Buffer sensor lower middle short circuit", "de": "Pufferfühler unten Mitte Kurzschluss"},
    "59": {"en": "Buffer sensor lower middle disconnected", "de": "Pufferfühler unten Mitte Unterbrechung"},
    # Verbrennung & Betrieb (26-50)
    "26": {"en": "Ignition time exceeded", "de": "Zündzeit überschritten"},
    "27": {"en": "Flue gas temperature too low", "de": "Rauchgastemperatur unterschritten"},
    "28": {"en": "System too long on O2 stop", "de": "Anlage zu lange auf O2-Stopp"},
    "29": {"en": "Combustion fault", "de": "Verbrennungsstörung"},
    "30": {"en": "Battery empty", "de": "Batterie leer"},
    "31": {"en": "Feed motor blocked", "de": "Blockade Einschubmotor"},
    "32": {"en": "Max fill time exceeded", "de": "Maximale Füllzeit überschritten"},
    "33": {"en": "Cleaning device not in rest position", "de": "Putzeinrichtung nicht in Ruhelage"},
    "38": {"en": "Overcurrent grate", "de": "Überstrom Schieberost"},
    "41": {"en": "Ash box almost full", "de": "Aschebox fast voll"},
    "42": {"en": "Overcurrent ash screw", "de": "Überstrom Ascheschnecke"},
    "43": {"en": "Ash conveyor not connected", "de": "Ascheaustragung nicht angeschlossen"},
    "45": {"en": "Return temperature not reached", "de": "Rücklaufanhebung Temperatur nicht erreicht"},
    "49": {"en": "Induced draft fan fault", "de": "Saugzuggebläse Störung"},
    "50": {"en": "Fill process timeout", "de": "Zeitüberschreitung Füllvorgang"},
    # Kommunikation & Module (62-99)
    "62": {"en": "GSM module not connected", "de": "GSM-Modul nicht angeschlossen"},
    "65": {"en": "GSM module send error", "de": "GSM-Modul Sendefehler"},
    "67": {"en": "Parameter error - factory defaults loaded", "de": "Fehler in Parametern, Werkseinstellungen geladen"},
    "70": {"en": "Pellet stock low", "de": "Pelletslagerstand gering"},
    "80": {"en": "Switching unit not connected", "de": "Umschalteinheit nicht angeschlossen"},
    "81": {"en": "Switching unit position 1 error", "de": "Positionsfehler Umschalteinheit Pos. 1"},
    "82": {"en": "Switching unit position 2 error", "de": "Positionsfehler Umschalteinheit Pos. 2"},
    "83": {"en": "Switching unit position 3 error", "de": "Positionsfehler Umschalteinheit Pos. 3"},
    "84": {"en": "Switching unit position 4 error", "de": "Positionsfehler Umschalteinheit Pos. 4"},
    "89": {"en": "Grate stiff", "de": "Schieberost schwergängig"},
    "90": {"en": "Boiler IO not connected", "de": "Kessel IO nicht angeschlossen"},
    "91": {"en": "Max board temperature exceeded", "de": "Max. Platinentemperatur überschritten"},
    "92": {"en": "Lambda probe not connected or defective", "de": "Lambdasonde nicht angeschlossen oder defekt"},
    "93": {"en": "Ash drawer open", "de": "Aschelade offen"},
    "94": {"en": "System set to Off - no frost protection", "de": "Betriebsart Aus, Frostschutz nicht gewährleistet"},
    "95": {"en": "Ash box switch must be bridged", "de": "Eingang Ascheboxschalter muss gebrückt werden"},
    "96": {"en": "Check power supply voltage", "de": "Spannung Netzteil kontrollieren"},
    "99": {"en": "Boiler overtemperature", "de": "Kessel Übertemperatur"},
    # Heizkreismodule (100-150)
    "100": {"en": "Heating circuit module CAN 1 not connected", "de": "Heizkreismodul CAN 1 nicht angeschlossen"},
    "103": {"en": "DHW sensor 3 short circuit", "de": "Boilerfühler 3 Kurzschluss"},
    "104": {"en": "DHW sensor 3 disconnected", "de": "Boilerfühler 3 Unterbrechung"},
    "107": {"en": "Flow sensor HC3 short circuit", "de": "Vorlauffühler HK3 Kurzschluss"},
    "108": {"en": "Flow sensor HC3 disconnected", "de": "Vorlauffühler HK3 Unterbrechung"},
    "109": {"en": "Flow sensor HC4 short circuit", "de": "Vorlauffühler HK4 Kurzschluss"},
    "110": {"en": "Flow sensor HC4 disconnected", "de": "Vorlauffühler HK4 Unterbrechung"},
    "111": {"en": "Room sensor HC3 short circuit", "de": "Raumfühler HK3 Kurzschluss"},
    "112": {"en": "Room sensor HC3 disconnected", "de": "Raumfühler HK3 Unterbrechung"},
    "113": {"en": "Room sensor HC4 short circuit", "de": "Raumfühler HK4 Kurzschluss"},
    "114": {"en": "Room sensor HC4 disconnected", "de": "Raumfühler HK4 Unterbrechung"},
    "120": {"en": "Heating circuit module CAN 2 not connected", "de": "Heizkreismodul CAN 2 nicht angeschlossen"},
    "127": {"en": "Flow sensor HC5 short circuit", "de": "Vorlauffühler HK5 Kurzschluss"},
    "128": {"en": "Flow sensor HC5 disconnected", "de": "Vorlauffühler HK5 Unterbrechung"},
    "129": {"en": "Flow sensor HC6 short circuit", "de": "Vorlauffühler HK6 Kurzschluss"},
    "130": {"en": "Flow sensor HC6 disconnected", "de": "Vorlauffühler HK6 Unterbrechung"},
    "131": {"en": "Room sensor HC5 short circuit", "de": "Raumfühler HK5 Kurzschluss"},
    "132": {"en": "Room sensor HC5 disconnected", "de": "Raumfühler HK5 Unterbrechung"},
    "133": {"en": "Room sensor HC6 short circuit", "de": "Raumfühler HK6 Kurzschluss"},
    "134": {"en": "Room sensor HC6 disconnected", "de": "Raumfühler HK6 Unterbrechung"},
    "140": {"en": "Heating circuit board CAN A not connected", "de": "Heizkreisplatine CAN A nicht angeschlossen"},
    "141": {"en": "Flow sensor HCA short circuit", "de": "Vorlauffühler HKA Kurzschluss"},
    "142": {"en": "Flow sensor HCA disconnected", "de": "Vorlauffühler HKA Unterbrechung"},
    "143": {"en": "DHW sensor A short circuit", "de": "Boilerfühler A Kurzschluss"},
    "144": {"en": "DHW sensor A disconnected", "de": "Boilerfühler A Unterbrechung"},
    "145": {"en": "Flow sensor remote line short circuit", "de": "Vorlauffühler geregelte Fernleitung Kurzschluss"},
    "146": {"en": "Flow sensor remote line disconnected", "de": "Vorlauffühler geregelte Fernleitung Unterbrechung"},
    "147": {"en": "Remote line board CAN F not connected", "de": "Fernleitungsplatine CAN F nicht angeschlossen"},
    "148": {"en": "Buffer board CAN C not connected", "de": "Pufferplatine CAN C nicht angeschlossen"},
    "149": {"en": "No connection to Loxone server", "de": "Keine Verbindung zu Loxone-Server"},
    "150": {"en": "Screed heating program deactivated", "de": "Estrich-Ausheizprogramm deaktiviert"},
    # Nano-PK Plus (153-161)
    "153": {"en": "No temperature rise (Nano-PK Plus)", "de": "Kein Temperaturanstieg (Nano-PK Plus)"},
    "154": {"en": "No temperature rise (Nano-PK Plus)", "de": "Kein Temperaturanstieg (Nano-PK Plus)"},
    "155": {"en": "Flushing defective (Nano-PK Plus)", "de": "Spülung defekt (Nano-PK Plus)"},
    "156": {"en": "Sensor Nano-PK Plus short circuit", "de": "Fühler Nano-PK Plus Kurzschluss"},
    "157": {"en": "Sensor Nano-PK Plus disconnected", "de": "Fühler Nano-PK Plus Unterbrechung"},
    "158": {"en": "No temperature rise after flushing", "de": "Kein Temperaturanstieg nach Spülung"},
    "159": {"en": "Flushing temperature not reached", "de": "Temperatur für Spülung nicht erreicht"},
    "160": {"en": "No communication with IO32 (AUE board)", "de": "Keine Kommunikation mit IO32 (AUE-Platine)"},
    "161": {"en": "No communication with motor board 0", "de": "Keine Kommunikation mit Motorplatine 0"},
    # Pellets-Positionen & Parametrierung (171-197)
    "171": {"en": "Pellet fill via position 1 not possible", "de": "Pellets füllen über Position 1 nicht möglich"},
    "172": {"en": "Pellet fill via position 2 not possible", "de": "Pellets füllen über Position 2 nicht möglich"},
    "173": {"en": "Pellet fill via position 3 not possible", "de": "Pellets füllen über Position 3 nicht möglich"},
    "174": {"en": "Pellet fill via position 4 not possible", "de": "Pellets füllen über Position 4 nicht möglich"},
    "175": {"en": "Pellet fill via position 5 not possible", "de": "Pellets füllen über Position 5 nicht möglich"},
    "176": {"en": "Pellet fill via position 6 not possible", "de": "Pellets füllen über Position 6 nicht möglich"},
    "177": {"en": "Pellet fill via position 7 not possible", "de": "Pellets füllen über Position 7 nicht möglich"},
    "178": {"en": "Pellet fill via position 8 not possible", "de": "Pellets füllen über Position 8 nicht möglich"},
    "179": {"en": "Request exceeds max temperature", "de": "Anforderung größer als Maximaltemperatur"},
    "180": {"en": "Check buffer sensor bottom position", "de": "Position Pufferfühler unten kontrollieren"},
    "190": {"en": "Check combustion - O2 target not reached", "de": "Verbrennung überprüfen, O2-Sollwert nicht erreicht"},
    "195": {"en": "Check system configuration urgently", "de": "Anlagenkonfiguration dringend überprüfen"},
    "196": {"en": "Burnout not completed multiple times", "de": "Ausbrand mehrmals nicht vollständig ausgeführt"},
    "197": {"en": "Check pump settings on boiler", "de": "Pumpeneinstellung am Kessel überprüfen"},
    # Externe Kontakte & Fernbedienungen (201-248)
    "201": {"en": "Check external contact wiring HC1", "de": "Kontrolle Beschaltung externer Kontakt HK1"},
    "202": {"en": "Check external contact wiring HC2", "de": "Kontrolle Beschaltung externer Kontakt HK2"},
    "203": {"en": "Check external contact wiring HC3", "de": "Kontrolle Beschaltung externer Kontakt HK3"},
    "204": {"en": "Check external contact wiring HC4", "de": "Kontrolle Beschaltung externer Kontakt HK4"},
    "205": {"en": "Check external contact wiring HC5", "de": "Kontrolle Beschaltung externer Kontakt HK5"},
    "206": {"en": "Check external contact wiring HC6", "de": "Kontrolle Beschaltung externer Kontakt HK6"},
    "210": {"en": "Remote FR35 HCA not connected", "de": "Fernbedienung FR35 HKA nicht angeschlossen"},
    "211": {"en": "Remote FR35 HC1 not connected", "de": "Fernbedienung FR35 HK1 nicht angeschlossen"},
    "212": {"en": "Remote FR35 HC2 not connected", "de": "Fernbedienung FR35 HK2 nicht angeschlossen"},
    "213": {"en": "Remote FR35 HC3 not connected", "de": "Fernbedienung FR35 HK3 nicht angeschlossen"},
    "214": {"en": "Remote FR35 HC4 not connected", "de": "Fernbedienung FR35 HK4 nicht angeschlossen"},
    "215": {"en": "Remote FR35 HC5 not connected", "de": "Fernbedienung FR35 HK5 nicht angeschlossen"},
    "216": {"en": "Remote FR35 HC6 not connected", "de": "Fernbedienung FR35 HK6 nicht angeschlossen"},
    "217": {"en": "Remote FR35 HCB not connected", "de": "Fernbedienung FR35 HKB nicht angeschlossen"},
    "220": {"en": "Remote FR40 HCA not connected", "de": "Fernbedienung FR40 HKA nicht angeschlossen"},
    "221": {"en": "Remote FR40 HC1 not connected", "de": "Fernbedienung FR40 HK1 nicht angeschlossen"},
    "222": {"en": "Remote FR40 HC2 not connected", "de": "Fernbedienung FR40 HK2 nicht angeschlossen"},
    "223": {"en": "Remote FR40 HC3 not connected", "de": "Fernbedienung FR40 HK3 nicht angeschlossen"},
    "224": {"en": "Remote FR40 HC4 not connected", "de": "Fernbedienung FR40 HK4 nicht angeschlossen"},
    "225": {"en": "Remote FR40 HC5 not connected", "de": "Fernbedienung FR40 HK5 nicht angeschlossen"},
    "226": {"en": "Remote FR40 HC6 not connected", "de": "Fernbedienung FR40 HK6 nicht angeschlossen"},
    "227": {"en": "Storage room switch off", "de": "Lagerraumschalter aus"},
    "228": {"en": "Pellet container almost empty", "de": "Pelletsbehälter fast leer"},
    "229": {"en": "Check level indicator", "de": "Füllstandsmelder kontrollieren"},
    "233": {"en": "Remote FR40 HCB not connected", "de": "Fernbedienung FR40 HKB nicht angeschlossen"},
    "240": {"en": "Remote control mismatch HCA", "de": "Fernbedienung stimmt nicht zur Parametrierung HKA"},
    "241": {"en": "Remote control mismatch HC1", "de": "Fernbedienung stimmt nicht zur Parametrierung HK1"},
    "242": {"en": "Remote control mismatch HC2", "de": "Fernbedienung stimmt nicht zur Parametrierung HK2"},
    "243": {"en": "Remote control mismatch HC3", "de": "Fernbedienung stimmt nicht zur Parametrierung HK3"},
    "244": {"en": "Remote control mismatch HC4", "de": "Fernbedienung stimmt nicht zur Parametrierung HK4"},
    "245": {"en": "Remote control mismatch HC5", "de": "Fernbedienung stimmt nicht zur Parametrierung HK5"},
    "246": {"en": "Remote control mismatch HC6", "de": "Fernbedienung stimmt nicht zur Parametrierung HK6"},
    "247": {"en": "Remote control mismatch HCB", "de": "Fernbedienung stimmt nicht zur Parametrierung HKB"},
    "248": {"en": "Check external request wiring", "de": "Kontrolle Beschaltung externe Anforderung"},
    # Kaskade & Kommunikation (230-236)
    "230": {"en": "Communication error to lead boiler", "de": "Kommunikationsfehler zu Führungskessel"},
    "231": {"en": "Follower boiler failed", "de": "Folgekessel ausgefallen"},
    "232": {"en": "Follower boiler fault", "de": "Folgekessel Störung"},
    "235": {"en": "CHP unit in fault or off", "de": "KWK in Störung oder auf Aus"},
    "236": {"en": "External boiler in fault or off", "de": "Fremdkessel in Störung oder auf Aus"},
    # Umschalteinheit & Motorplatine (250-262)
    "250": {"en": "Switching unit motor board not connected", "de": "Motorplatine Umschalteinheit nicht angeschlossen"},
    "251": {"en": "Switching unit motor not connected", "de": "Motor Umschalteinheit nicht angeschlossen"},
    "252": {"en": "Switching unit position not reached", "de": "Umschalteinheit erreicht Position nicht"},
    "253": {"en": "AUP motor short circuit", "de": "Motor AUP Kurzschluss"},
    "254": {"en": "AUP motor board overtemperature", "de": "Motorplatine AUP Übertemperatur"},
    "255": {"en": "AUP motor board undervoltage 24V", "de": "Motorplatine AUP Unterspannung 24V"},
    "256": {"en": "Switching unit not in position", "de": "Umschalteinheit nicht in Position"},
    "260": {"en": "DRM AHF board not connected", "de": "DRM AHF-Platine nicht angeschlossen"},
    "261": {"en": "DRM AHF board phase sequence wrong", "de": "DRM AHF-Platine Phasenfolge falsch"},
    "262": {"en": "Room auger motor not connected or fuse defective", "de": "Motor Raumaustragung nicht angeschlossen oder Sicherung defekt"},
    "275": {"en": "Confirm to continue - cause: STB", "de": "Zum Fortsetzen Meldung quittieren, Ursache: STB"},
    # Differenzregler (280-297)
    "280": {"en": "Differential controller CAN D not connected", "de": "Differenzregler CAN D nicht angeschlossen"},
    "281": {"en": "Heat source sensor S1 short circuit", "de": "Wärmequellenfühler S1 Kurzschluss"},
    "282": {"en": "Heat source sensor S1 disconnected", "de": "Wärmequellenfühler S1 Unterbrechung"},
    "283": {"en": "Reference sensor S2 short circuit", "de": "Referenzfühler S2 Kurzschluss"},
    "284": {"en": "Reference sensor S2 disconnected", "de": "Referenzfühler S2 Unterbrechung"},
    "285": {"en": "Return sensor external boiler short circuit", "de": "Rücklauffühler Fremdwärmekessel Kurzschluss"},
    "286": {"en": "Return sensor external boiler disconnected", "de": "Rücklauffühler Fremdwärmekessel Unterbrechung"},
    "287": {"en": "Return temp external boiler not reached", "de": "Rücklauftemperatur Fremdwärmekessel nicht erreicht"},
    "290": {"en": "Differential controller 2 CAN 9 not connected", "de": "Differenzregler 2 CAN 9 nicht angeschlossen"},
    "291": {"en": "Heat source sensor S3 short circuit", "de": "Wärmequellenfühler S3 Kurzschluss"},
    "292": {"en": "Heat source sensor S3 disconnected", "de": "Wärmequellenfühler S3 Unterbrechung"},
    "293": {"en": "Reference sensor S4 short circuit", "de": "Referenzfühler S4 Kurzschluss"},
    "294": {"en": "Reference sensor S4 disconnected", "de": "Referenzfühler S4 Unterbrechung"},
    "295": {"en": "Return sensor external boiler 2 short circuit", "de": "Rücklauffühler Fremdwärmekessel 2 Kurzschluss"},
    "296": {"en": "Return sensor external boiler 2 disconnected", "de": "Rücklauffühler Fremdwärmekessel 2 Unterbrechung"},
    "297": {"en": "Return temp external boiler 2 not reached", "de": "Rücklauftemperatur Fremdwärmekessel 2 nicht erreicht"},
    # Kessel ID & Lagerraum (305-332)
    "305": {"en": "Wrong boiler ID card", "de": "Falsche Kessel ID-Card"},
    "314": {"en": "Ash screw blocked", "de": "Ascheschnecke blockiert"},
    "322": {"en": "Boiler ID card not connected", "de": "Kessel ID-Card nicht angeschlossen"},
    "332": {"en": "Storage room switch activated", "de": "Lagerraumschalter betätigt"},
    # HKR-Verbindungen (355-370)
    "355": {"en": "No connection to HKR 0", "de": "Keine Verbindung zu HKR 0"},
    "356": {"en": "No connection to HKR 1", "de": "Keine Verbindung zu HKR 1"},
    "357": {"en": "No connection to HKR 2", "de": "Keine Verbindung zu HKR 2"},
    "358": {"en": "No connection to HKR 3", "de": "Keine Verbindung zu HKR 3"},
    "359": {"en": "No connection to HKR 4", "de": "Keine Verbindung zu HKR 4"},
    "360": {"en": "No connection to HKR 5", "de": "Keine Verbindung zu HKR 5"},
    "361": {"en": "No connection to HKR 6", "de": "Keine Verbindung zu HKR 6"},
    "362": {"en": "No connection to HKR 7", "de": "Keine Verbindung zu HKR 7"},
    "363": {"en": "No connection to HKR 8", "de": "Keine Verbindung zu HKR 8"},
    "364": {"en": "No connection to HKR 9", "de": "Keine Verbindung zu HKR 9"},
    "365": {"en": "No connection to HKR 10", "de": "Keine Verbindung zu HKR 10"},
    "366": {"en": "No connection to HKR 11", "de": "Keine Verbindung zu HKR 11"},
    "367": {"en": "No connection to HKR 12", "de": "Keine Verbindung zu HKR 12"},
    "368": {"en": "No connection to HKR 13", "de": "Keine Verbindung zu HKR 13"},
    "369": {"en": "No connection to HKR 14", "de": "Keine Verbindung zu HKR 14"},
    "370": {"en": "No connection to HKR 15", "de": "Keine Verbindung zu HKR 15"},
    # Wartung & Brennraum (371-398)
    "371": {"en": "Check combustion chamber", "de": "Brennraum prüfen"},
    "380": {"en": "Service due - factory maintenance required", "de": "Wartung fällig, Werkswartung durchführen lassen"},
    "381": {"en": "Suction turbine runtime - replace carbon brushes", "de": "Laufzeit Saugturbine, Schleifkohlen tauschen"},
    "390": {"en": "Heat source sensor (board S, S4) short circuit", "de": "Wärmequellenfühler (Platine S, S4) Kurzschluss"},
    "391": {"en": "Heat source sensor (board S, S4) disconnected", "de": "Wärmequellenfühler (Platine S, S4) Unterbrechung"},
    "392": {"en": "Reference sensor (board S, S3) short circuit", "de": "Referenzfühler (Platine S, S3) Kurzschluss"},
    "393": {"en": "Reference sensor (board S, S3) disconnected", "de": "Referenzfühler (Platine S, S3) Unterbrechung"},
    "394": {"en": "Return sensor external boiler 3 short circuit", "de": "Rücklauffühler Fremdwärmekessel 3 Kurzschluss"},
    "395": {"en": "Return sensor external boiler 3 disconnected", "de": "Rücklauffühler Fremdwärmekessel 3 Unterbrechung"},
    "396": {"en": "Return temp external boiler 3 not reached", "de": "Rücklauftemperatur Fremdwärmekessel 3 nicht erreicht"},
    "397": {"en": "Reference sensor (board S, S2) short circuit", "de": "Referenzfühler (Platine S, S2) Kurzschluss"},
    "398": {"en": "Reference sensor (board S, S2) disconnected", "de": "Referenzfühler (Platine S, S2) Unterbrechung"},
    # Frischwasserstation (422-498)
    "422": {"en": "Flow sensor FWS 1 short circuit", "de": "Vorlauffühler FWS 1 Kurzschluss"},
    "423": {"en": "Flow sensor FWS 1 disconnected", "de": "Vorlauffühler FWS 1 Unterbrechung"},
    "424": {"en": "Flow sensor FWS 2 short circuit", "de": "Vorlauffühler FWS 2 Kurzschluss"},
    "425": {"en": "Flow sensor FWS 2 disconnected", "de": "Vorlauffühler FWS 2 Unterbrechung"},
    "426": {"en": "Flow sensor FWS 3 short circuit", "de": "Vorlauffühler FWS 3 Kurzschluss"},
    "427": {"en": "Flow sensor FWS 3 disconnected", "de": "Vorlauffühler FWS 3 Unterbrechung"},
    "428": {"en": "Flow sensor FWS 4 short circuit", "de": "Vorlauffühler FWS 4 Kurzschluss"},
    "429": {"en": "Flow sensor FWS 4 disconnected", "de": "Vorlauffühler FWS 4 Unterbrechung"},
    "440": {"en": "Heating circuit board CAN B not connected", "de": "Heizkreisplatine CAN B nicht angeschlossen"},
    "441": {"en": "Flow sensor HCB short circuit", "de": "Vorlauffühler HKB Kurzschluss"},
    "442": {"en": "Flow sensor HCB disconnected", "de": "Vorlauffühler HKB Unterbrechung"},
    "443": {"en": "DHW sensor B short circuit", "de": "Boilerfühler B Kurzschluss"},
    "444": {"en": "DHW sensor B disconnected", "de": "Boilerfühler B Unterbrechung"},
    "450": {"en": "Smart-HV not connected", "de": "Smart-HV nicht angeschlossen"},
    "452": {"en": "Smart combi master/slave config wrong", "de": "Smart-Kombi Parametrierung Master/Slave falsch"},
    "453": {"en": "Smart combi fault", "de": "Smart-Kombi Störung"},
    "480": {"en": "Buffer temp for DHW 1 too low", "de": "Puffertemperatur für Warmwasser 1 unterschritten"},
    "481": {"en": "Buffer temp for DHW 2 too low", "de": "Puffertemperatur für Warmwasser 2 unterschritten"},
    "482": {"en": "Buffer temp for DHW 3 too low", "de": "Puffertemperatur für Warmwasser 3 unterschritten"},
    "483": {"en": "Buffer temp for DHW 4 too low", "de": "Puffertemperatur für Warmwasser 4 unterschritten"},
    "487": {"en": "Circulation pump could not be calibrated", "de": "Zirkulationspumpe konnte nicht angelernt werden"},
    "488": {"en": "Flow sensor FWS short circuit", "de": "Vorlauffühler FWS Kurzschluss"},
    "489": {"en": "Flow sensor FWS disconnected", "de": "Vorlauffühler FWS Unterbrechung"},
    "490": {"en": "FWS 1 temperature sensor disconnected", "de": "Frischwasserstation 1 Temperaturfühler Unterbrechung"},
    "492": {"en": "FWS 1 temperature sensor short circuit", "de": "Frischwasserstation 1 Temperaturfühler Kurzschluss"},
    "493": {"en": "FWS 2 temperature sensor disconnected", "de": "Frischwasserstation 2 Temperaturfühler Unterbrechung"},
    "494": {"en": "FWS 2 temperature sensor short circuit", "de": "Frischwasserstation 2 Temperaturfühler Kurzschluss"},
    "495": {"en": "FWS 3 temperature sensor disconnected", "de": "Frischwasserstation 3 Temperaturfühler Unterbrechung"},
    "496": {"en": "FWS 3 temperature sensor short circuit", "de": "Frischwasserstation 3 Temperaturfühler Kurzschluss"},
    "497": {"en": "FWS 4 temperature sensor disconnected", "de": "Frischwasserstation 4 Temperaturfühler Unterbrechung"},
    "498": {"en": "FWS 4 temperature sensor short circuit", "de": "Frischwasserstation 4 Temperaturfühler Kurzschluss"},
    # Erweiterungsplatinen IO-X10 (540-571)
    "540": {"en": "Extension board 0 not connected", "de": "IO-X10-104 Erweiterungsplatine 0 nicht angeschlossen"},
    "541": {"en": "Extension board 1 not connected", "de": "IO-X10-104 Erweiterungsplatine 1 nicht angeschlossen"},
    "542": {"en": "Extension board 2 not connected", "de": "IO-X10-104 Erweiterungsplatine 2 nicht angeschlossen"},
    "543": {"en": "Extension board 3 not connected", "de": "IO-X10-104 Erweiterungsplatine 3 nicht angeschlossen"},
    "544": {"en": "Extension board 4 not connected", "de": "IO-X10-104 Erweiterungsplatine 4 nicht angeschlossen"},
    "545": {"en": "Extension board 5 not connected", "de": "IO-X10-104 Erweiterungsplatine 5 nicht angeschlossen"},
    "546": {"en": "Extension board 6 not connected", "de": "IO-X10-104 Erweiterungsplatine 6 nicht angeschlossen"},
    "547": {"en": "Extension board 7 not connected", "de": "IO-X10-104 Erweiterungsplatine 7 nicht angeschlossen"},
    "548": {"en": "Extension board 8 not connected", "de": "IO-X10-104 Erweiterungsplatine 8 nicht angeschlossen"},
    "549": {"en": "Extension board 9 not connected", "de": "IO-X10-104 Erweiterungsplatine 9 nicht angeschlossen"},
    "570": {"en": "Extension board A not connected", "de": "IO-X10-104 Erweiterungsplatine A nicht angeschlossen"},
    "571": {"en": "Extension board B not connected", "de": "IO-X10-104 Erweiterungsplatine B nicht angeschlossen"},
    # System & Protokoll (902-910)
    "902": {"en": "Error log initialized", "de": "Fehlerspeicher initialisiert"},
    "903": {"en": "Restart (Power ON)", "de": "Neustart (Power ON)"},
    "910": {"en": "Write to dongle failed", "de": "Schreiben auf Dongle fehlgeschlagen"},
    # Fernleitungsplatine (1100-1102)
    "1100": {"en": "Remote line board CAN 0 not connected", "de": "Fernleitungsplatine CAN 0 nicht angeschlossen"},
    "1101": {"en": "Flow sensor remote line 2 short circuit", "de": "Vorlauffühler geregelte Fernleitung 2 Kurzschluss"},
    "1102": {"en": "Flow sensor remote line 2 disconnected", "de": "Vorlauffühler geregelte Fernleitung 2 Unterbrechung"},
    # Hardware-Test Störungen (4020-5275)
    "4020": {"en": "Room auger motor not connected", "de": "Raumschnecke Motor nicht angeschlossen"},
    "4030": {"en": "Fuse F15 defective", "de": "Sicherung F15 defekt"},
    "4120": {"en": "Suction turbine not connected", "de": "Saugturbine nicht angeschlossen"},
    "4130": {"en": "Fuse F21 defective (suction turbine)", "de": "Sicherung F21 defekt (Saugturbine)"},
    "4220": {"en": "Fuse F13 defective", "de": "Sicherung F13 defekt"},
    "4230": {"en": "Fuse F17 defective", "de": "Sicherung F17 defekt"},
    "4250": {"en": "Fuse F21 defective", "de": "Sicherung F21 defekt"},
    "4320": {"en": "Feed motor not connected", "de": "Einschubmotor nicht angeschlossen"},
    "4330": {"en": "Fuse F18 defective", "de": "Sicherung F18 defekt"},
    "4420": {"en": "Induced draft motor not connected", "de": "Saugzugmotor nicht angeschlossen"},
    "4430": {"en": "Fuse F20 defective", "de": "Sicherung F20 defekt"},
    "4630": {"en": "Fuse F19 defective (ignition)", "de": "Sicherung F19 defekt (Zündung)"},
    "4720": {"en": "Ignition not connected", "de": "Zündung nicht angeschlossen"},
    "4820": {"en": "Cleaning device not connected", "de": "Putzeinrichtung nicht angeschlossen"},
    "5020": {"en": "Grate drive not connected", "de": "Schieberost nicht angeschlossen"},
    "5120": {"en": "Room auger 2 motor not connected", "de": "Motor Raumaustragung 2 nicht angeschlossen"},
    "5220": {"en": "HC1 pump not connected or safety thermostat triggered", "de": "HK1 Pumpe nicht angeschlossen oder Sicherheitsthermostat ausgelöst"},
    "5270": {"en": "Overcurrent room auger 1 - check auger and turbine", "de": "Überstrom Raumaustragungsschnecke 1, Saugturbine überprüfen"},
    "5275": {"en": "Thermal protection room auger 1", "de": "Thermoschutz Raumaustragungsschnecke 1"},
}

# Firmware versions
# IMPORTANT: Keep this list in sync with FIRMWARE_TEMPLATES in src/firmware_templates.py
# When adding a new firmware version:
# 1. Add the XML template to FIRMWARE_TEMPLATES in src/firmware_templates.py
# 2. Add the version string here
# 3. Run tools/parameter_validator.py to verify consistency
FIRMWARE_VERSIONS: Final = [
    "V14_1HAR_q1",
    "V14_1HAR_q1_solar",  # Nano.2 20 + Solar/3HK extension (Issue #11)
    "V14_0HAR_q",
    "V14_0m5",  # Classic Lambda 40L-60L
    "V14_0d",  # HSV/CL 9-60KW (Issue #14)
    "V40_0HAR_az15",  # Nano 65
]

# Energy calculation defaults
DEFAULT_PELLET_ENERGY: Final = 4.8  # kWh per kg (Heizwert)
DEFAULT_EFFICIENCY: Final = 90  # % Wirkungsgrad
