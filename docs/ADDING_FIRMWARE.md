# Adding New Firmware Version Support

This guide explains how to add support for additional Hargassner firmware versions to the integration using the automated DAQ parser tool.

## Table of Contents

- [Overview](#overview)
- [Quick Start (4 Steps)](#quick-start-4-steps)
- [Schritt 1: Firmware-Version ablesen](#schritt-1-firmware-version-ablesen)
- [Schritt 2: SD-Karten-Logging aktivieren](#schritt-2-sd-karten-logging-aktivieren)
- [Schritt 3: DAQ-Datei auslesen](#schritt-3-daq-datei-auslesen)
- [Schritt 4: Code einfügen](#schritt-4-code-einfügen)
- [Testing and Validation](#testing-and-validation)
- [Troubleshooting](#troubleshooting)
- [Contributing Your Template](#contributing-your-template)

---

## Overview

The integration uses XML-based firmware templates (DAQPRJ format) to parse telnet messages from different boiler firmware versions. Each firmware version may have different parameter positions, names, and data formats.

**Architecture:**
```
Boiler → DAQ File on SD Card → DAQ Parser Tool → Firmware Template → Integration
```

**The Easy Way:** Hargassner boilers automatically log all parameter definitions to SD card in DAQ files. Our `daq_parser.py` tool extracts everything automatically - no manual analysis needed!

## Quick Start (4 Steps)

### Prerequisites

- ✅ Access to your Hargassner boiler
- ✅ Python 3.8+ installed
- ✅ This integration's source code

### Total Time: ~10 minutes

1. **Firmware-Version am Kessel-Display ablesen** (1 min)
2. **SD-Karten-Logging für einige Minuten aktivieren** (5 min)
3. **DAQ-Datei mit Tool auslesen und Python-Code generieren** (2 min)
4. **Python-Code an richtigen Stellen einfügen** (2 min)

Fertig! ✨

---

## Schritt 1: Firmware-Version ablesen

### Am Kessel-Display

1. Gehe zum Hauptmenü deines Hargassner-Kessels
2. Navigiere zu **Service** oder **Info**
3. Suche nach **Software-Version** oder **Firmware**
4. Notiere die Version (z.B. `V14.1HAR.q1`, `V15.2HAR`, etc.)

**Beispiel:**
```
Software: V14.1HAR.q1
Hardware: V1.0
```

Diese Version benötigst du später für die Benennung im Code.

---

## Schritt 2: SD-Karten-Logging aktivieren

### 2.1 SD-Karte einlegen

Falls noch keine SD-Karte im Kessel ist:
- Öffne das Bedienfeld des Kessels
- Lege eine SD-Karte ein (in der Regel hinter einer kleinen Klappe)
- Der Kessel beginnt automatisch mit dem Logging

### 2.2 Logging laufen lassen

**Wichtig:** Lasse den Kessel für mindestens **5-10 Minuten** laufen, während die SD-Karte eingelegt ist.

Der Kessel schreibt kontinuierlich DAQ-Dateien mit allen Parameter-Definitionen und Messwerten.

### 2.3 SD-Karte entnehmen

Nach 5-10 Minuten:
- Öffne das Bedienfeld
- Entnimm die SD-Karte
- Stecke sie in deinen Computer (SD-Kartenleser)

**Hinweis:** Der Kessel kann ohne SD-Karte weiterlaufen, loggt dann aber keine neuen Daten.

---

## Schritt 3: DAQ-Datei auslesen

### 3.1 DAQ-Datei finden

Auf der SD-Karte findest du Dateien wie:
```
DAQ00000.DAQ
DAQ00001.DAQ
DAQ00002.DAQ
```

**Welche Datei?** Nimm die **neueste** DAQ-Datei (höchste Nummer oder neuestes Datum).

Typische Dateigröße: 1-10 MB

### 3.2 DAQ Parser ausführen

Öffne ein Terminal/Kommandozeile und navigiere zum `tools`-Ordner der Integration:

**Windows:**
```bash
cd C:\Temp\nano_pk\tools
python daq_parser.py E:\DAQ00000.DAQ --output python > firmware_template.txt
```

**Linux/macOS:**
```bash
cd /path/to/IP-HargassnerIntegration/tools
python3 daq_parser.py /media/sd-card/DAQ00000.DAQ --output python > firmware_template.txt
```

**Hinweis:** Ersetze den Pfad zur DAQ-Datei mit dem tatsächlichen Pfad auf deinem System (z.B. `E:\DAQ00000.DAQ` wenn die SD-Karte als Laufwerk E: eingebunden ist).

### 3.3 Generierter Code

Das Tool erstellt automatisch eine Datei `firmware_template.txt` mit fertigem Python-Code:

**Beispiel-Output:**

```python
"""
Firmware Template: V14_1HAR_q1
Generated from DAQ file

System Information:
- Manufacturer: Hargassner
- Model: Nano-PK 32
- Software: V14.1HAR.q1
- Hardware: V1.0
- Serial: 123456

Statistics:
- Analog Parameters: 112
- Digital Parameters: 116
- Expected Message Length: 138
"""

# Add to FIRMWARE_TEMPLATES in firmware_templates.py
FIRMWARE_TEMPLATES["V14_1HAR_q1"] = """<DAQPRJ>
  <ANALOG>
    <CHANNEL id="0" name="ZK" dop="" unit="" />
    <CHANNEL id="3" name="TK" dop="" unit="°C" />
    <CHANNEL id="8" name="TRG" dop="" unit="°C" />
    <!-- ... alle weiteren Parameter ... -->
  </ANALOG>
  <DIGITAL>
    <CHANNEL id="102" bit="0" name="M1_Kessel_Geblaese" />
    <!-- ... alle weiteren Bits ... -->
  </DIGITAL>
</DAQPRJ>"""

# Add to FIRMWARE_VERSIONS in const.py
FIRMWARE_VERSIONS.append("V14_1HAR_q1")
```

Dieser Code enthält:
- ✅ Komplettes DAQPRJ-XML-Template mit allen Parametern
- ✅ System-Informationen (Hersteller, Modell, Version)
- ✅ Statistiken (Anzahl Parameter, Message-Länge)
- ✅ Fertige Code-Snippets zum Einfügen

---

## Schritt 4: Code einfügen

Jetzt fügst du den generierten Code an zwei Stellen ein:

### 4.1 Datei 1: firmware_templates.py

Öffne: `custom_components/bauergroup_hargassnerintegration/src/firmware_templates.py`

**Was einfügen:** Die komplette Zeile mit `FIRMWARE_TEMPLATES["..."] = """<DAQPRJ>...</DAQPRJ>"""`

**Wo einfügen:** In das Dictionary `FIRMWARE_TEMPLATES`, unterhalb der bestehenden Einträge.

**Beispiel:**

```python
FIRMWARE_TEMPLATES = {
    # Existing firmware
    "V14_1HAR_q1": """<DAQPRJ>
        <!-- existing template -->
    </DAQPRJ>""",

    # Deine neue Firmware (aus firmware_template.txt kopieren)
    "V15_2HAR": """<DAQPRJ>
        <!-- HIER DEN KOMPLETTEN DAQPRJ-BLOCK EINFÜGEN -->
    </DAQPRJ>""",
}
```

**Tipp:** Kopiere einfach die komplette Zeile aus `firmware_template.txt` und füge sie vor der schließenden `}` ein.

### 4.2 Datei 2: const.py

Öffne: `custom_components/bauergroup_hargassnerintegration/const.py`

**Was einfügen:** Die Firmware-Version als String

**Wo einfügen:** In die Liste `FIRMWARE_VERSIONS`

**Beispiel:**

```python
FIRMWARE_VERSIONS: Final = [
    "V14_1HAR_q1",
    "V15_2HAR",      # Deine neue Version hier hinzufügen
]
```

**Wichtig:** Der Name muss **exakt identisch** sein mit dem Dictionary-Key in `firmware_templates.py`!

### 4.3 Fertig!

Das war's! Du hast erfolgreich:

- ✅ DAQPRJ-XML-Template in `firmware_templates.py` eingefügt
- ✅ Firmware-Version in `const.py` hinzugefügt

Jetzt kannst du die Integration testen.

---

## Testing and Validation

Nach dem Einfügen des Codes musst du die Integration testen.

### 5.1 Home Assistant neustarten

```bash
# Via Home Assistant UI
Settings → System → Restart
```

### 5.2 Debug Logging aktivieren (optional)

Füge in `configuration.yaml` ein:

```yaml
logger:
  default: info
  logs:
    custom_components.bauergroup_hargassnerintegration: debug
```

Starte Home Assistant erneut.

### 5.3 Integration mit neuer Firmware hinzufügen

1. Gehe zu **Einstellungen → Geräte & Dienste**
2. Klicke **Integration hinzufügen**
3. Suche nach **"Bauergroup Hargassner"**
4. Konfiguriere:
   - **Host:** IP-Adresse deines Kessels
   - **Firmware:** Wähle deine neue Firmware-Version
   - **Sensor Set:** Starte mit **STANDARD**
5. Klicke **Absenden**

### 5.4 Sensoren überprüfen

Prüfe, dass die Sensoren korrekte Werte anzeigen:

1. **Einstellungen → Geräte & Dienste → Deine Integration**
2. Klicke auf die Integration, um alle Entitäten zu sehen
3. Vergleiche Sensorwerte mit dem Kessel-Display:
   - Kesseltemperatur sollte übereinstimmen
   - Außentemperatur sollte übereinstimmen
   - Kesselzustand sollte übereinstimmen
   - Werte sollten alle 5 Sekunden aktualisiert werden

### 5.5 Logs prüfen

**Einstellungen → System → Protokolle**

Erwartete Meldungen:
- ✅ `Successfully connected to boiler`
- ✅ `Parsed message with X parameters`
- ❌ Keine Parsing-Fehler oder "Unknown state" Warnungen

**Beispiel-Logs:**

```
[custom_components.bauergroup_hargassnerintegration.src.telnet_client] Successfully connected to 192.168.1.100:23
[custom_components.bauergroup_hargassnerintegration.src.message_parser] Parsed message with 138 values
[custom_components.bauergroup_hargassnerintegration.coordinator] Data update successful
```

### 5.6 Validierung mit Tools (optional)

Prüfe die Template-Konsistenz:

```bash
cd tools
python parameter_validator.py
```

Das Tool prüft:
- XML ist valide
- Keine duplizierten Parameter
- Namenskonventionen eingehalten
- Alle Standard-Parameter vorhanden

### 5.7 Erweiterte Tests

Lasse die Integration 24 Stunden laufen, um sicherzustellen:
- Verbindung bleibt stabil
- Keine Memory Leaks
- Alle Sensorwerte aktualisieren korrekt
- Keine unerwarteten Fehler in Logs

---

## Troubleshooting

### Issue: "Failed to parse DAQPRJ XML"

**Cause:** XML syntax error in template

**Solution:**
- Validate the XML using an online validator
- Ensure you copied the complete `<DAQPRJ>...</DAQPRJ>` block
- Check for special characters or encoding issues

### Issue: "Firmware version not found"

**Cause:** Version name mismatch between `const.py` and `firmware_templates.py`

**Solution:**
- Ensure the dictionary key in `FIRMWARE_TEMPLATES` matches exactly the string in `FIRMWARE_VERSIONS`
- Version names are case-sensitive

### Issue: Sensors show "Unknown" state

**Cause:** Parameter not found in telnet message

**Solution:**
- Enable debug logging
- Check logs for message length: `Parsed message with X values`
- Verify DAQ file is from the same boiler you're connecting to
- Some parameters may not be available on all configurations

### Issue: Wrong sensor values

**Cause:** Parameter index mismatch or wrong firmware template

**Solution:**
- Double-check you're using the correct firmware version in config
- Verify the DAQ file matches your boiler model and firmware
- Compare a few key values manually:
  - Boiler temperature should be index 3 in most firmwares
  - Outside temperature is usually index 20
  - Check boiler display to validate

### Issue: DAQ parser fails to extract DAQPRJ

**Cause:** DAQ file is corrupted or wrong format

**Solution:**
- Try a different DAQ file from the SD card
- Ensure file was copied completely (check file size)
- Try `--output text` to see what information is available
- Check file isn't encrypted (older firmwares may use different formats)

### Issue: Integration won't load after adding template

**Cause:** Python syntax error in `firmware_templates.py`

**Solution:**
- Check Home Assistant logs for Python traceback
- Ensure XML string is properly enclosed in `""" ... """`
- Verify commas between dictionary entries
- No trailing commas after last entry

---

## Contributing Your Template

Once you've tested your firmware template and confirmed it works, please contribute it back to help others!

### How to Contribute

1. **Fork the repository** on GitHub
2. **Add your template** to `firmware_templates.py`
3. **Add firmware version** to `const.py`
4. **Add sample DAQ file** (optional) to `docs/firmware_samples/`
5. **Update README** to list supported firmware version
6. **Submit pull request** with description:
   - Firmware version
   - Boiler model
   - Testing duration
   - Any quirks or special notes

### What to Include

**Required:**
- Firmware template in `firmware_templates.py`
- Version string in `const.py`

**Recommended:**
- Sample DAQ file (first 100 lines) in `docs/firmware_samples/YOUR_VERSION.txt`
- Screenshot of working sensors in `docs/images/`
- Notes about any special configuration

**Template for Pull Request:**
```markdown
# Add support for firmware V15.2HAR

- **Firmware:** V15.2HAR
- **Boiler Model:** Nano-PK 32
- **Testing Duration:** 7 days
- **Sensors:** 112 analog, 116 digital
- **Notes:** Works identically to V14.1HAR.q1

Tested on production system without issues.
```

### Testing Checklist Before Contributing

- ✅ Template loads without errors
- ✅ All sensors show correct values
- ✅ Tested for at least 24 hours
- ✅ No errors in Home Assistant logs
- ✅ Validated with `parameter_validator.py`
- ✅ Connection remains stable
- ✅ Energy sensor calculates correctly

---

## Additional Resources

### Tools Documentation

See [tools/README.md](../tools/README.md) for detailed information about:
- `daq_parser.py` - DAQ file parser
- `telnet_tester.py` - Telnet connection tester
- `message_generator.py` - Test message generator
- `parameter_validator.py` - Template validator

### Integration Documentation

- **[Architecture Overview](ARCHITECTURE.md)** - Technical deep-dive
- **[Development Guide](DEVELOPMENT.md)** - Developer setup and workflow
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute

### Getting Help

If you encounter issues:

1. **Check logs:** Enable debug logging and review Home Assistant logs
2. **Validate template:** Run `parameter_validator.py`
3. **Test connection:** Use `telnet_tester.py` to verify connectivity
4. **Ask for help:**
   - Open an issue: https://github.com/bauer-group/IP-HargassnerIntegration/issues
   - Include: Firmware version, DAQ parser output, error messages, logs
5. **Community discussion:** https://github.com/bauer-group/IP-HargassnerIntegration/discussions

---

**Your contributions make this integration better for everyone! 🙏**

Last Updated: 2025-11-23
