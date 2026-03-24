# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [0.3.2] - UNRELEASED

### 🐛 Fixed

- **Pelletverbrauch-Hochrechnung: HDD-Berechnung monatsgenau statt Tagesdurchschnitt**
  - Sensor `hdd_norm_zeitraum` verwendete einen flachen Durchschnitt (`2798 / 365 ≈ 7,67 HDD/Tag`), unabhängig von der saisonalen Verteilung
  - Im Winter (Hauptmessperiode) wurden die HDD massiv unterschätzt → Effizienz (kg/HDD) viel zu hoch → alle Prognosen um Faktor 5–10× überhöht
  - Neuer Sensor summiert die anteiligen VDI 4710 Norm-HDD monatsweise vom Startdatum bis heute (Start-/Endmonat tagesgenau anteilig)
  - Betrifft: Jahresprognose, Monatsprognose, Restjahr-Prognose, Effizienz kg/HDD

- **Pelletverbrauch-Hochrechnung: Startwert-Offset für kumulativen Zähler**
  - Neuer `input_number.hg_pk32_pelletverbrauch_startwert` Helper speichert den Zählerstand bei Messbeginn
  - Effizienz-Sensor berechnet jetzt `(aktueller Zähler - Startwert) / HDD` statt `Zähler / HDD`
  - Verhindert Verfälschung bei Zählerständen die nicht bei 0 beginnen

### ✨ Improved

- **Dashboard YAML aktualisiert** auf den aktuellen Produktiv-Stand
  - Kessel-Solltemperatur, Puffer-Sollwerte (Min/Max) in der Übersicht ergänzt
  - Heizraum-Temperatursensoren (THD-005) hinzugefügt
  - ApexCharts 30-Tage-Übersicht mit optimierter Konfiguration (yaxis, transform, columnWidth)
  - Warmwasser-Entity auf `warmwasser_b` korrigiert

## [0.3.1] - 2026-03-12

### 🐛 Fixed

- **Fehlende/falsche Fehlercodes + Fallback für unbekannte Codes** ([Issue #16](https://github.com/bauer-group/IP-HargassnerIntegration/issues/16))
  - Community-Beitrag von [@mkaufmann0983](https://github.com/mkaufmann0983)
  - `ERROR_CODES` von 15 auf 294 Einträge erweitert (Quelle: offizielles Hargassner Nano-PK Manual)
  - Fehlercode 380 korrigiert: "Wartung fällig, Werkswartung durchführen lassen"
  - Dynamischer Fallback für unbekannte Fehlercodes — verhindert "Unknown"-Status in Home Assistant

## [0.3.0] - 2026-03-03

### ✨ Added

- **Firmware-Unterstützung für HSV/CL 9-60KW (V14_0d)** ([Issue #14](https://github.com/bauer-group/IP-HargassnerIntegration/issues/14))
  - Community-Beitrag von [@tk79](https://github.com/tk79)
  - 165 Analog-Parameter, 84 Digital-Parameter
  - Ältestes unterstütztes Modell (HSV 15.2, ~10 Jahre alt)
  - Kaskaden-Parameter, Betriebsstundenzähler (BSZ), Mengenwärmezähler (MWZ)
  - Encoding-Artefakt `H°Chste Anf` → `Höchste Anf` korrigiert
  - ⚠️ **Hinweis**: V14_0d hat keinen `Störungs Nr` Analog-Parameter — der Betriebsstatus-Sensor zeigt immer "OK". Störungen werden nur als digitaler Bit-Wert übertragen.

### ✨ Improved

- **30+ neue Parameter-Beschreibungen (DE/EN)** für V14_0d
  - Mengenwärmezähler (MWZ), Betriebsstundenzähler (BSZ), Schieberost, VFS, Kaskade

## [0.2.9] - 2026-03-03

### ✨ Added

- **Firmware-Unterstützung für Nano.2 20 + Solar/3HK (V14_1HAR_q1_solar)** ([Issue #11](https://github.com/bauer-group/IP-HargassnerIntegration/issues/11))
  - Community-Beitrag von [@tvieider](https://github.com/tvieider) via DAQ-Template
  - 132 Analog-Parameter (inkl. 3 Dummy-Kanäle für Board-Alignment)
  - Solar-Parameter: DiffR3TWq, DiffR3 K1/K2, DiffR3TDiff1/TDiff2, DiffR3 P1/P2/P3, DiffR3 WMZ
  - AUP-Parameter: AUPSoll, AUPIst, AUPStrom
  - Füllstand und BoiZustand_1

- **Firmware-Unterstützung für Nano 65 (V40_0HAR_az15)** ([PR #13](https://github.com/bauer-group/IP-HargassnerIntegration/pull/13))
  - Community-Beitrag von [@marianhoenscheid](https://github.com/marianhoenscheid)

### 🐛 Fixed

- **Cross-Template Parameter-Kompatibilität** ([Issue #12](https://github.com/bauer-group/IP-HargassnerIntegration/issues/12))
  - Neues `_PARAM_NAME_ALIASES`-System in [sensor.py](custom_components/bauergroup_hargassnerintegration/sensor.py) für bidirektionale Umlaut↔ASCII Zuordnung
  - Wärmemenge-Sensor funktioniert jetzt korrekt mit V14_0HAR_q Template (`Verbrauchszaehler` ↔ `Verbrauchszähler`)
  - Störungs-Sensor Lookup korrigiert (`Storungs Nr` ↔ `Störungs Nr`)
  - V14_0HAR_q Tippfehler `Storungs Nr` bewusst beibehalten für Entity-ID-Stabilität

- **DAQ-Parser Encoding verbessert** ([tools/daq_parser.py](tools/daq_parser.py))
  - CP1252 als primäres Encoding priorisiert (Windows-Standard für DAQ-Dateien)
  - Sonderzeichen (°, ä, ö, ü) werden jetzt korrekt gelesen statt ersetzt

### ✨ Improved

- **FULL-Modus Anzeigenamen für V14_0HAR_q** ([firmware_templates.py](custom_components/bauergroup_hargassnerintegration/firmware_templates.py))
  - ASCII-Varianten in `PARAMETER_DESCRIPTIONS` ergänzt (Verbrauchszaehler, Stoerungs Nr, Puff Fuellgrad, etc.)
  - FULL-Modus zeigt jetzt korrekte zweisprachige Beschreibungen statt Roh-Parameternamen

## [0.2.8] - 2026-01-19

### 🐛 Fixed

- **V14_0HAR_q Template: Heizkreis-Parameter korrigiert** ([Issue #10](https://github.com/bauer-group/IP-HargassnerIntegration/issues/10))
  - Vorlauf-Ist und Vorlauf-Soll Positionen für HK1/HK2 korrigiert
  - Neuer Parameter `HK1 Status` bei Position 65 hinzugefügt
  - Korrigierte Zuordnung: Position 66 = TVL_1 (Vorlauf Ist), Position 67 = TVLs_1 (Vorlauf Soll)
  - Community-Feedback von [@MiOrt](https://github.com/MiOrt) mit Telnet-Analyse

- **V14_0HAR_q Template: Sonderzeichen normalisiert** ([Issue #9](https://github.com/bauer-group/IP-HargassnerIntegration/issues/9))
  - `Verbrauchsz°hler` → `Verbrauchszaehler`
  - `Störung` → `Stoerung`
  - `Puff Füllgrad` → `Puff Fuellgrad`
  - `T Spülung` → `T Spuelung`
  - `LZ ES seit F°ll.` → `LZ ES seit Fuell.`
  - Entity-IDs jetzt sauber ohne `deg`-Artefakte

### 📚 Docs

- **Dokumentation für Input DateTime Helper** ([Issue #5](https://github.com/bauer-group/IP-HargassnerIntegration/issues/5))
  - Neuer Schritt 2 in [CUSTOM_DASHBOARD.md](docs/CUSTOM_DASHBOARD.md): Anleitung zur Erstellung des `input_datetime.hg_pk32_pelletverbrauch_startzeit` Helpers
  - Option A (UI) und Option B (YAML) dokumentiert
  - Troubleshooting-Abschnitt für Prognose-Sensoren hinzugefügt

## [0.2.7] - 2026-01-12

### ✨ Added

- **Firmware-Unterstützung für Classic Lambda 40L-60L (V14_0m5)** ([firmware_templates.py](custom_components/bauergroup_hargassnerintegration/firmware_templates.py))
  - Community-Beitrag von [@philippe44](https://github.com/philippe44) via [Issue #6](https://github.com/bauer-group/IP-HargassnerIntegration/issues/6)
  - 146 Analog-Parameter (vs. ~112 beim Nano-PK)
  - Unterstützung für Heizkreise 3-6
  - Zusätzliche Warmwasser-Sensoren (TB2, TB3)
  - Firmware-Version in [const.py](custom_components/bauergroup_hargassnerintegration/const.py) registriert

- **Classic-spezifische Parameter-Beschreibungen (DE/EN)** ([firmware_templates.py](custom_components/bauergroup_hargassnerintegration/firmware_templates.py))
  - 60+ neue Parameter-Übersetzungen für Classic Lambda
  - Puffer Mitte-Oben/Unten (TPmo, TPmu)
  - Heizkreise 3-6 vollständig (TVL, TVLs, TRA, TRs, HKZustand, FR Zustand)
  - Externe Heizkreis-Pumpen (EHKP, EHKP2, EHKP3)

### 🐛 Fixed

- **Sprachunterstützung für STANDARD_SENSORS** ([sensor.py](custom_components/bauergroup_hargassnerintegration/sensor.py))
  - Community-Beitrag von [@philippe44](https://github.com/philippe44) via [PR #7](https://github.com/bauer-group/IP-HargassnerIntegration/pull/7)
  - STANDARD_SENSORS verwenden jetzt sprachabhängige Namen aus `PARAMETER_DESCRIPTIONS`
  - Englischsprachige Benutzer sehen nun korrekt übersetzte Sensornamen
  - Entity-IDs bleiben stabil (kein Breaking Change)

## [0.2.6] - 2025-12-01

### 🐛 Fixed

- **Kritischer Reconnect-Bug behoben**: Endlose Reconnect-Schleife korrigiert ([telnet_client.py](custom_components/bauergroup_hargassnerintegration/telnet_client.py))
  - **Problem**: `_last_update` wurde bei `_close_connection()` nicht zurückgesetzt, was zu sofortiger erneuter Staleness-Erkennung nach Reconnect führte (13.000+ Reconnects)
  - **Fix 1**: `_last_update = None` bei Verbindungsabbruch setzen
  - **Fix 2**: Delay nach Staleness-Disconnect hinzugefügt (`TELNET_RECONNECT_DELAY`)
  - **Fix 3**: Initiale Verbindung wird nicht mehr als Reconnection gezählt

## [0.2.5] - 2025-11-29

### ✨ Added

- **Erweitertes Standard-Sensor-Set**: Von 17 auf 27 Sensoren erweitert ([sensor.py](custom_components/bauergroup_hargassnerintegration/sensor.py))
  - Kessel Solltemperatur (TKsoll)
  - Brennraumtemperatur (BRT)
  - Wirkungsgrad (Effizienz)
  - O2 Gehalt (O2)
  - Saugzug Ist (SZist)
  - Puffer Sollwert Oben/Unten (Puffer_soll oben/unten)
  - Vorlauf Soll Heizkreis 1 (TVLs_1)
  - Warmwasser Soll (TBs_1)

### 📚 Docs

- Dokumentation für erweitertes Standard-Sensor-Set aktualisiert
  - README.md, SCHNELLSTART.md, ARCHITECTURE.md, INSTALLATION.md, PROJECT_SUMMARY.md
- Code-Dokumentation in sensor.py verbessert mit Übersicht aller Standard-Sensoren

## [0.2.4] - 2025-11-29

### 🐛 Fixed

- **Reconnect-Mechanismus**: Vereinfacht und korrigiert ([telnet_client.py](custom_components/bauergroup_hargassnerintegration/telnet_client.py))
  - Entfernt: Komplexe consecutive-timeout Logik und exponential backoff die HA-Prozess überlasteten
  - Reconnect nur bei: TCP-Verbindungsverlust (OS-Level) oder 60s keine Daten empfangen
  - Einfacher 5s Reconnect-Delay zwischen Versuchen

- **Störungs-Sensor**: Vereinfacht ([sensor.py](custom_components/bauergroup_hargassnerintegration/sensor.py))
  - Verwendet nur noch `Störungs Nr`: 0 = OK, >0 = Störungscode

- **Sensorwerte bei Verbindungsverlust**: Zeigen jetzt "unknown" statt alte Werte ([coordinator.py](custom_components/bauergroup_hargassnerintegration/coordinator.py))
  - Bei Verbindungsverlust werden Sensordaten gelöscht
  - Sensoren gehen auf "unknown" bis neue Daten empfangen werden

- **Firmware V14_1HAR_q1**: Warmwasser-Parameter korrigiert ([firmware_templates.py](custom_components/bauergroup_hargassnerintegration/firmware_templates.py))
  - `TB1` (Warmwasser Ist) und `TBs_1` (Warmwasser Soll) waren vertauscht

### ✨ Improved

- **Release Script**: Verwendet jetzt CHANGELOG-Inhalt für GitHub Release Notes ([release.py](release.py))
  - Extrahiert automatisch den Abschnitt für die jeweilige Version aus CHANGELOG.md
  - Fallback auf Link zum CHANGELOG wenn kein Abschnitt gefunden

### 🗑️ Removed

- Nicht mehr benötigte Konstanten: `TELNET_MAX_RECONNECT_DELAY`, `TELNET_MAX_CONSECUTIVE_TIMEOUTS` ([const.py](custom_components/bauergroup_hargassnerintegration/const.py))

## [0.2.3] - 2025-11-28

### 🐛 Fixed

- Home Assistant Deprecation-Warnungen behoben (Issues [#2](https://github.com/bauer-group/IP-HargassnerIntegration/issues/2), [#3](https://github.com/bauer-group/IP-HargassnerIntegration/issues/3))
  - **OptionsFlow**: Explizites Setzen von `self.config_entry` entfernt ([config_flow.py](custom_components/bauergroup_hargassnerintegration/config_flow.py)) - deprecated in HA 2025.12
  - **DataUpdateCoordinator**: `config_entry` Parameter zu `super().__init__()` hinzugefügt ([coordinator.py](custom_components/bauergroup_hargassnerintegration/coordinator.py)) - erforderlich für `async_config_entry_first_refresh()` seit HA 2025.11

### 📚 Docs

- HACS Install-Button zu README.md, SCHNELLSTART.md und docs/INSTALLATION.md hinzugefügt

## [0.2.2] - 2025-11-27

### ✨ Improved

- Sensor-Updates auf Push-Modus umgestellt ([coordinator.py](custom_components/bauergroup_hargassnerintegration/coordinator.py))
  - **Push**: Sofortige Updates bei jedem empfangenen Datensatz vom Kessel (keine Messdaten verloren)
  - **Manueller Poll**: `_async_update_data()` verfügbar für manuelle Refresh-Aufrufe
  - Connection-Callback hinzugefügt für robuste Verbindungsstatus-Erkennung ([telnet_client.py](custom_components/bauergroup_hargassnerintegration/telnet_client.py))

## [0.2.1] - 2025-11-27

### 🐛 Fixed

- Verbindungserkennung bei Stromausfall des Kessels korrigiert ([telnet_client.py](custom_components/bauergroup_hargassnerintegration/telnet_client.py))
  - **Problem**: Nach Stromausfall meldete Integration weiterhin "verbunden", obwohl Verbindung tot war
  - Konsekutive Timeout-Zählung: Nach 3 aufeinanderfolgenden Timeouts (30s) wird Verbindung als tot erkannt
  - Daten-Staleness-Prüfung: Automatischer Reconnect wenn 60s keine Daten empfangen (Kessel sendet alle paar Sekunden)
  - TCP-Keepalive aktiviert: OS-Level Erkennung toter Verbindungen (Linux: 30s idle, dann alle 10s prüfen)
  - Neue Konstanten in [const.py](custom_components/bauergroup_hargassnerintegration/const.py#L29): `TELNET_MAX_CONSECUTIVE_TIMEOUTS`, `TELNET_DATA_STALENESS_TIMEOUT`

## [0.2.0] - 2025-11-25

### ✨ Added

- Firmware-Unterstützung für V14_0HAR_q hinzugefügt
  - Community-Beitrag von [@notecp](https://github.com/notecp)
  - Template in [firmware_templates.py](custom_components/bauergroup_hargassnerintegration/firmware_templates.py#L23) hinzugefügt
  - Firmware-Version in [const.py](custom_components/bauergroup_hargassnerintegration/const.py) registriert
  - [README.md](README.md) aktualisiert mit Status "Community tested - use at own risk"

## [0.1.2] - 2025-11-25

### 🐛 Fixed

- Korrektur der Firmware-Template für V14_1HAR_q1
  - Fehlende digitale Parameter IDs 5 und 8 hinzugefügt als Reserved-Slots
  - Erwartete Nachrichtenlänge jetzt korrekt: 121 Werte (112 analog + 9 digital)
  - Längenprüfungs-Warnung auf Debug-Level herabgestuft ([message_parser.py](custom_components/bauergroup_hargassnerintegration/message_parser.py#L174))
  - Template und Beschreibungen aktualisiert ([firmware_templates.py](custom_components/bauergroup_hargassnerintegration/firmware_templates.py#L22))

## [0.1.0] - 2025-11-22

### ✨ Added

Erste Release-Kandidat Version der Bauergroup Hargassner Integration.

- **Thread-safe Telnet Client** mit Auto-Reconnect
  - Exponential backoff (5s → 300s)
  - Multi-Encoding Support (UTF-8, Latin-1, CP1252)
  - Background asyncio task für kontinuierlichen Empfang
- **Config Flow** für GUI-basierte Konfiguration
  - Connection validation
  - Firmware-Auswahl (V14_1HAR_q1)
  - Sprach-Auswahl (EN/DE)
  - Sensor-Set Auswahl (STANDARD/FULL)
- **Data Update Coordinator** für effizienten Datenabruf (5 Sekunden Intervall)
- **Type Definitions** (`types.py`) für strukturierte Datentypen
- **Custom Exceptions** (`exceptions.py`) für besseres Error Handling
- **138 Parameter vollständig dokumentiert**
  - Alle Heizkreise (A, 1-6)
  - Alle Warmwasser-Kreise (A, 1-3)
  - Lambda-Sonde Parameter
  - Motor-Ströme
  - Buffer-Sensoren
  - Kategorisiert und strukturiert
- **16 Standard-Sensoren** (13 Parameter + 4 Spezial-Sensoren)
  - Connection Status (Verbindung)
  - Boiler State (Kesselzustand) mit dynamischem Icon
  - Operation Status (Betriebsstatus/Fehlercode)
  - Heat Output (Wärmemenge) - Energy Dashboard kompatibel
  - 13 vordefinierte Parameter-Sensoren (Temperaturen, Leistung, Vorrat, etc.)
- **FULL-Modus**: Alle Firmware-Parameter als Sensoren
  - Dynamisch basierend auf Firmware-Template
  - Automatische Device Class Zuordnung (°C → Temperatur, etc.)
  - Zweisprachige Beschreibungen (EN/DE)
- **Development Tools** im `tools/` Verzeichnis
  - `daq_parser.py` - Extrahiert Firmware-Templates aus DAQ-Dateien
  - `message_generator.py` - Generiert Test-Nachrichten
  - `parameter_validator.py` - Validiert Konsistenz der Parameter
  - `telnet_tester.py` - Testet Telnet-Verbindung
- **Umfassende Dokumentation**
  - ARCHITECTURE.md (Technische Architektur)
  - INSTALLATION.md (Installationsanleitung)
  - DEVELOPMENT.md (Entwickler-Leitfaden)
  - CONTRIBUTING.md (Beitrags-Richtlinien)
  - ADDING_FIRMWARE.md / ADDING_FIRMWARE_DE.md (Firmware-Hinzufügen Anleitung)
  - VERSIONING.md (Semantic Versioning Guidelines)
  - COMMIT_GUIDELINES.md (Conventional Commits Standard)
- **Übersetzungen** (Englisch, Deutsch)
- **Firmware Support**
  - V14_1HAR_q1 vollständig unterstützt

### 🔧 Technical

- Async/await Architektur durchgängig
- Type hints 100%
- Moderne Home Assistant Best Practices
- Saubere Code-Struktur mit src/-Verzeichnis
- Error Handling auf allen Ebenen
- Thread-safe Data Access mit asyncio.Lock

---

## Links

- [VERSIONING.md](VERSIONING.md) - Semantic Versioning Guidelines
- [COMMIT_GUIDELINES.md](COMMIT_GUIDELINES.md) - Commit Message Standard
- [README.md](README.md) - Projekt-Übersicht
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technische Architektur
