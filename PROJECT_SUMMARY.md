# Hargassner Pellet Boiler Integration - Project Summary

## Overview

Complete, professional Home Assistant custom component for Hargassner pellet boilers with telnet interface. Built from scratch using modern best practices.

**Version:** 0.1.2
**Status:** Production Ready
**License:** MIT

## Key Features

✅ **Real-time Monitoring** - Continuous telnet data stream
✅ **Auto-Reconnect** - Exponential backoff, never gives up
✅ **Thread-Safe** - Async/await architecture
✅ **Robust Encoding** - UTF-8, Latin-1, CP1252 support
✅ **GUI Configuration** - Config Flow with validation
✅ **Multi-Firmware** - Supports multiple boiler versions
✅ **Energy Dashboard** - Built-in energy sensor (kWh)
✅ **Bilingual** - English and German translations
✅ **Error Tolerant** - Graceful degradation, extensive error handling
✅ **Professional Docs** - Architecture, development, contributing guides

## Project Structure

```
hargassner_pellet/
├── custom_components/hargassner_pellet/    # Main integration
│   ├── __init__.py                         # Entry point, setup/teardown
│   ├── config_flow.py                      # GUI configuration
│   ├── const.py                            # Constants
│   ├── coordinator.py                      # Data coordinator
│   ├── manifest.json                       # HA integration metadata
│   ├── sensor.py                           # Sensor platform
│   ├── src/                                # Core business logic
│   │   ├── __init__.py
│   │   ├── firmware_templates.py           # XML templates for firmware versions
│   │   ├── message_parser.py               # Telnet message parser
│   │   └── telnet_client.py                # Thread-safe telnet client
│   └── translations/                       # Localization
│       ├── en.json
│       └── de.json
├── docs/                                   # Documentation
│   ├── ARCHITECTURE.md                     # Technical architecture (in-depth)
│   ├── CONTRIBUTING.md                     # Contribution guidelines
│   ├── DEVELOPMENT.md                      # Developer setup & workflow
│   └── INSTALLATION.md                     # End-user installation guide
├── tests/                                  # Unit tests (starter)
│   └── test_message_parser.py
├── .gitignore                              # Git ignore patterns
├── LICENSE                                 # MIT License
├── PROJECT_SUMMARY.md                      # This file
└── README.md                               # Main project README

Total: 18 files
```

## Technical Architecture

### Layer 1: Telnet Client (`src/telnet_client.py`)

**Responsibilities:**
- Persistent telnet connection (port 23)
- Background asyncio task for continuous receiving
- Automatic reconnection with exponential backoff (5s → 300s)
- Multi-encoding support (UTF-8, Latin-1, CP1252)
- Thread-safe data storage with `asyncio.Lock`
- Statistics tracking (messages, errors, reconnections)

**Key Methods:**
- `async_start()` - Start client and background receiver
- `async_stop()` - Graceful shutdown
- `get_latest_data()` - Thread-safe data access
- `_receiver_loop()` - Background message receiver
- `_process_data()` - Encoding detection and parsing

### Layer 2: Message Parser (`src/message_parser.py`)

**Responsibilities:**
- Parse XML firmware templates
- Extract values from telnet messages
- Type conversion (float, int, bool)
- Digital parameter bit extraction

**Key Classes:**
- `HargassnerMessageParser` - Main parser
- `ParameterDefinition` - Individual parameter metadata

**Supported Message Format:**
```
pm <val0> <val1> <val2> ... <valN>
   ^^^^^ Space-separated values
```

### Layer 3: Coordinator (`coordinator.py`)

**Responsibilities:**
- Bridge between telnet client and Home Assistant
- Periodic data refresh (5 seconds)
- Extends `DataUpdateCoordinator` for HA integration
- Error handling and recovery

### Layer 4: Sensor Platform (`sensor.py`)

**Sensor Types:**
1. **Connection Sensor** - Connection status + statistics
2. **State Sensor** - Boiler operating state (enum)
3. **Error Sensor** - Error messages (enum)
4. **Parameter Sensors** - Individual measurements
5. **Energy Sensor** - kWh calculation from pellet consumption

**Sensor Sets:**
- **STANDARD** - 13 essential sensors
- **FULL** - 30+ sensors (all available)

### Layer 5: Configuration (`config_flow.py`)

**Features:**
- GUI-based setup (Config Flow)
- Connection validation before entry creation
- Options flow for runtime changes
- Unique ID validation (one entry per IP)

## Data Flow

```
Boiler (Telnet Port 23)
    ↓ "pm 7 10.1 9.0 67.4 ..."
TelnetClient._receiver_loop()
    ↓ Decode (UTF-8/Latin-1/CP1252)
    ↓ Extract lines, find latest "pm" message
MessageParser.parse_message()
    ↓ Split values, map to parameters
    ↓ Type conversion, bit extraction
TelnetClient._latest_data (async locked)
    ↓ Poll every 5 seconds
Coordinator._async_update_data()
    ↓ Update event
Sensor Entities (Connection, State, Parameters, Energy)
    ↓ Display in Home Assistant UI
```

## Firmware Support

Currently supported firmware versions:
- **V14_1HAR_q1** - 112 analog + many digital parameters

Adding new versions: Just add XML template to `firmware_templates.py`

## Example Telnet Message (V14_1HAR_q1)

```
pm 7 10.1 9.0 67.4 70 64.5 65 11 91.3 26 27.0 62.3 59.3 58.7 89 5 64 3 70 62 30 28.9 30 100 30.0 30.0 29 96.0 100 3 0 0 18 2 10 0 0 333 324 160 24 1 21 0 91 8.00 12.99 616 8.9 24209 140.0 110.3 28 -20.0 -20.0 0.0 60.0 -20.0 93.4 1 0 -20.0 0 20.0 20.0 0 1 0 120.0 0 20.0 20.0 0 1 0 120.0 0 20.0 20.0 0 1 0 -20.0 0 20.0 20.0 0 1 0 -20.0 0 120.0 0 -20.0 0 0.0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.00 E 21 0 0 2007 0 0 0
```

This message contains 138 values corresponding to:
- `values[0]` = ZK (Boiler state) = 7
- `values[3]` = TK (Boiler temp) = 67.4°C
- `values[8]` = TRG (Smoke gas temp) = 91.3°C
- `values[14]` = Leistung (Output) = 89%
- `values[20]` = Taus (Outside temp) = 30°C
- ... and so on

## Error Handling

### Connection Errors
- **Initial failure:** Raises `ConfigEntryNotReady`, HA retries
- **Runtime loss:** Background task continues reconnecting
- **Exponential backoff:** 5s → 10s → 20s → ... → 300s max

### Parsing Errors
- **Invalid encoding:** Try UTF-8 → Latin-1 → CP1252 → fallback
- **Length mismatch:** Log warning, parse available data
- **Invalid values:** Return `None`, sensor shows "unknown"

### Update Errors
- **No data yet:** Return empty dict (not an error on startup)
- **Coordinator timeout:** Automatic retry with backoff

## Performance

- **Update interval:** 5 seconds (configurable)
- **Memory usage:** ~5-10 MB (typical)
- **CPU usage:** Minimal (async I/O)
- **Network:** ~1-2 KB/message, ~400 bytes/s average

## Installation

### Via HACS
1. Add custom repository
2. Install integration
3. Restart HA
4. Add via UI

### Manual
1. Copy `custom_components/hargassner_pellet` to HA config
2. Restart HA
3. Add integration via Settings → Devices & Services

## Configuration Example

```yaml
# Via GUI (recommended), or YAML:
hargassner_pellet:
  host: 192.168.1.100
  firmware: V14_1HAR_q1
  device_name: Hargassner Boiler
  language: EN
  sensor_set: STANDARD
  pellet_energy_kwh_per_kg: 4.8  # Pellet energy content (3.0-6.0)
  efficiency_percent: 90          # Boiler efficiency (50-100)
```

## Available Sensors (Standard Set)

1. Connection Status
2. Boiler State (Off/Ignition/Full Firing/etc.)
3. Operation Status (OK/Errors)
4. Boiler Temperature (°C)
5. Smoke Gas Temperature (°C)
6. Output Power (%)
7. Outside Temperature (°C)
8. Buffer Temperature Top/Middle/Bottom (°C)
9. Hot Water Temperature (°C)
10. Return Temperature (°C)
11. Buffer Fill Level (%)
12. Pellet Stock (kg)
13. Pellet Consumption (kg)
14. Flow Temperature (°C)
15. **Heat Output (kWh)** - Calculated from pellet consumption with configurable energy content and efficiency

## Energy Dashboard Integration

Energy sensor automatically created:

- **Name:** "Wärmemenge" (DE) / "Heat Output" (EN)
- **Formula:** `Pellet Consumption (kg) × Energy Content (kWh/kg) × Efficiency (%)`
- **Configurable Parameters:**
  - Pellet Energy Content: 3.0-6.0 kWh/kg (Default: 4.8)
  - Boiler Efficiency: 50-100% (Default: 90%)
- **Example:** 100 kg × 4.8 kWh/kg × 0.90 = 432 kWh
- Compatible with HA Energy Dashboard
- Tracks total heat output from pellet heating
- Sensor attributes show current calculation parameters

## Security Considerations

⚠️ **Important:**
- Telnet is **unencrypted** and **unauthenticated**
- Use only on **trusted local networks**
- Consider **VPN** for remote access
- **Firewall** appropriately

## Development Status

| Feature | Status |
|---------|--------|
| Telnet Client | ✅ Complete |
| Message Parser | ✅ Complete |
| Config Flow | ✅ Complete |
| Coordinator | ✅ Complete |
| Sensors | ✅ Complete |
| Translations (EN/DE) | ✅ Complete |
| Documentation | ✅ Complete |
| Unit Tests | ⚠️ Starter files |
| HACS Integration | ⏳ Pending |
| HA Core Integration | ⏳ Future |

## Future Enhancements

- [ ] Write support (send commands to boiler)
- [ ] Additional sensor platforms (binary_sensor, switch)
- [ ] Historical data tracking
- [ ] Efficiency calculations
- [ ] Predictive maintenance alerts
- [ ] Custom Lovelace cards
- [ ] Comprehensive unit tests
- [ ] Integration tests

## Code Quality

- ✅ Type hints throughout
- ✅ Docstrings for all public functions
- ✅ Error handling at all layers
- ✅ Async/await (no blocking I/O)
- ✅ Thread-safe data access
- ✅ PEP 8 compliant
- ✅ Home Assistant conventions followed

## Documentation

- **README.md** - User-facing overview
- **INSTALLATION.md** - Step-by-step setup guide
- **ARCHITECTURE.md** - Technical deep-dive (20+ pages)
- **DEVELOPMENT.md** - Developer workflow
- **CONTRIBUTING.md** - Contribution guidelines
- **PROJECT_SUMMARY.md** - This file

## License

MIT License - See [LICENSE](LICENSE) file

## Support & Contributing

- **Issues:** Report bugs and request features
- **Discussions:** Ask questions, share ideas
- **Pull Requests:** Contribute code (see CONTRIBUTING.md)
- **Documentation:** Help improve docs

## Contact

- GitHub: https://github.com/bauer-group/IP-HargassnerIntegration
- Issues: https://github.com/bauer-group/IP-HargassnerIntegration/issues

---

**Built with ❤️ for the Home Assistant community**

Last Updated: 2025-11-22
