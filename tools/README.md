# Development Tools

Tools für Entwickler zur Arbeit mit der Hargassner Integration.

## DAQ Parser

### Beschreibung

Der `daq_parser.py` extrahiert Firmware-Templates und System-Informationen aus DAQ-Dateien, die vom Hargassner Kessel auf SD-Karte gespeichert werden.

### Verwendung

```bash
# Basis-Analyse (Text-Ausgabe)
python daq_parser.py <daq-datei>

# JSON-Ausgabe
python daq_parser.py <daq-datei> --output json

# Python Code für Integration
python daq_parser.py <daq-datei> --output python
```

### Beispiele

```bash
# Analysiere DAQ-Datei
python daq_parser.py ../docs/sdcard_log_samples/DAQ00000.DAQ

# Erzeuge Python Template-Code
python daq_parser.py DAQ00000.DAQ --output python > new_firmware.txt

# Export als JSON
python daq_parser.py DAQ00000.DAQ --output json > firmware_data.json
```

### Was wird extrahiert?

1. **System-Information:**
   - Hersteller, Modell
   - Software/Hardware-Version
   - Seriennummern
   - Betriebsstunden

2. **DAQPRJ XML-Template:**
   - Komplettes XML für `firmware_templates.py`
   - Analog-Parameter (mit ID, Name, Einheit)
   - Digital-Parameter (mit ID, Bit, Name)

3. **Telnet-Nachrichten (Samples):**
   - Beispiel-Messages für Tests
   - Format: `pm <wert1> <wert2> ...`

### Neue Firmware-Version hinzufügen

**Schritt 1:** DAQ-Datei vom Kessel holen
- SD-Karte aus Kessel entfernen
- DAQ-Datei kopieren (z.B. `DAQ00000.DAQ`)

**Schritt 2:** Template extrahieren
```bash
python daq_parser.py DAQ00000.DAQ --output python
```

**Schritt 3:** Output in `firmware_templates.py` einfügen
- FIRMWARE_TEMPLATES Dictionary erweitern
- Version in FIRMWARE_VERSIONS Liste hinzufügen

**Schritt 4:** Parameter-Beschreibungen ergänzen
- In `PARAMETER_DESCRIPTIONS` neue Parameter hinzufügen
- Beschreibungen anhand Kessel-Manual ergänzen

**Schritt 5:** Testen
```bash
# Mit echten Telnet-Daten testen
# Sensoren in Home Assistant prüfen
```

### Ausgabe-Formate

#### Text (Standard)
```
==================================================================
DAQ FILE ANALYSIS
==================================================================

SYSTEM INFORMATION:
  Manufacturer:      Hargassner
  Model:             Nano.2 32
  Software Version:  V14.1HAR.q1
  ...

PARAMETER STATISTICS:
  Analog Parameters:  112
  Digital Parameters: 116
  ...
```

#### JSON
```json
{
  "system_info": {
    "manufacturer": "Hargassner",
    "model": "Nano.2 32",
    "software_version": "V14.1HAR.q1",
    ...
  },
  "daqprj_template": "<DAQPRJ>...</DAQPRJ>",
  "analog_parameters": [...],
  ...
}
```

#### Python
```python
# Add to FIRMWARE_TEMPLATES in firmware_templates.py
FIRMWARE_TEMPLATES["V14_1HAR_q1"] = """<DAQPRJ>...</DAQPRJ>"""

# Add to FIRMWARE_VERSIONS in const.py
FIRMWARE_VERSIONS.append("V14_1HAR_q1")
```

## Telnet Tester

### Beschreibung

Der `telnet_tester.py` testet die Telnet-Verbindung zum Hargassner Kessel und zeigt Echtzeit-Nachrichten an.

### Verwendung

```bash
# Basis-Test (unbegrenzt)
python telnet_tester.py <ip-adresse>

# 10 PM-Nachrichten empfangen
python telnet_tester.py <ip-adresse> --count 10

# 30 Sekunden lang empfangen
python telnet_tester.py <ip-adresse> --duration 30

# Custom Port und Timeout
python telnet_tester.py <ip-adresse> --port 23 --timeout 5
```

### Beispiele

```bash
# Grundlegende Verbindung testen
python telnet_tester.py 192.168.1.100

# 20 Nachrichten mit 5s Timeout
python telnet_tester.py 192.168.1.100 --count 20 --timeout 5
```

### Was wird angezeigt?

1. **Verbindungsstatus** - Erfolg/Fehler mit Hinweisen
2. **Echtzeit-Nachrichten** - Alle empfangenen pm-Nachrichten
3. **Statistiken:**
   - Laufzeit
   - Anzahl Nachrichten (total und PM)
   - Bytes empfangen
   - Nachrichten/Sekunde

### Verwendungszwecke

- Netzwerk-Konnektivität prüfen
- Telnet-Port Erreichbarkeit testen
- Nachrichtenformat überprüfen
- Datenrate messen

---

## Message Generator

### Beschreibung

Der `message_generator.py` generiert protokollgültige Test-Nachrichten aus einem Firmware-Template.

Die Nachricht wird direkt aus dem DAQPRJ-Template aufgebaut und hat daher immer exakt die Werteanzahl, die der Parser für diese Firmware erwartet: erst der Analog-Block (eine Position je `ANALOG`-Kanal-`id`), dann die Digital-Words (je `DIGITAL`-`id` ein Word, als Grossbuchstaben-Hex).

### Verwendung

```bash
# Standard-Test-Nachricht generieren
python message_generator.py

# 10 Nachrichten mit Leistungsbrand-Zustand
python message_generator.py --count 10 --state heating

# Custom Firmware-Version
python message_generator.py --firmware V14_1HAR_q1 --count 5
```

### Beispiele

```bash
# Eine Nachricht im Aus-Zustand
python message_generator.py --state off

# 20 Nachrichten im Zünd-Zustand
python message_generator.py --count 20 --state ignition

# Verschiedene Zustände rotierend
python message_generator.py --count 50
```

### Parameter

- `--firmware`, `-f` - Firmware-Version (default: V14_1HAR_q1)
- `--count`, `-c` - Anzahl Nachrichten (default: 1)
- `--state`, `-s` - Kessel-Zustand (default: rotierend über alle Zustände):
  - `off` - Aus (ZK 1)
  - `ignition` - Zündung (ZK 5)
  - `heating` - Leistungsbrand (ZK 7)
  - `cleaning` - Reinigung (ZK 12)
- `--format`, `-o` - Ausgabeformat: `text` (default) oder `json`
- `--seed` - Startwert des Zufallsgenerators, für reproduzierbare Ausgabe in Tests

### Verwendungszwecke

- Parser-Tests ohne echten Kessel
- Sensor-Verhalten simulieren
- Entwicklung ohne Hardware
- Testdaten für Unit-Tests

---

## Parameter Validator

### Beschreibung

Der `parameter_validator.py` validiert die Konsistenz zwischen Firmware-Templates und Parameter-Beschreibungen.

### Verwendung

```bash
# Standard-Validierung
python parameter_validator.py

# Mit verbose Output
python parameter_validator.py --verbose
```

### Was wird geprüft?

1. **Template-Parsing** - Können alle Templates geparst werden?
2. **Parameter-Beschreibungen** - Sind alle Parameter beschrieben?
3. **Duplikate** - Gibt es doppelte Parameter in Templates?
4. **Namenskonventionen** - Sind Parameter-Namen konsistent?

### Ausgabe

```
==================================================================
PARAMETER VALIDATION
==================================================================

Checking template parsing...
Checking parameter descriptions...
Checking for duplicates...
Checking naming conventions...

==================================================================
RESULTS
==================================================================

WARNINGS:
  [WARN] 5 parameters without descriptions:
    - NewParam1
    - NewParam2
    ...

SUMMARY:
  Errors:   0
  Warnings: 1

[WARN] Validation passed with warnings
```

### Verwendungszwecke

- Nach Hinzufügen neuer Firmware-Versionen
- Vor Release Parameter-Konsistenz prüfen
- Fehlende Beschreibungen finden
- Code-Qualität sicherstellen
