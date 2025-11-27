# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

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
