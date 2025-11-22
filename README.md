# Hargassner Pellet Boiler Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Modern, professional Home Assistant integration for Hargassner pellet boilers with telnet interface.

## Features

- **Real-time monitoring** of boiler parameters via telnet
- **Automatic reconnection** with exponential backoff
- **Thread-safe** telnet client with background message processing
- **Robust error handling** and encoding support (UTF-8, Latin-1, CP1252)
- **GUI configuration** via Home Assistant UI (Config Flow)
- **Firmware support** for V14_1HAR_q1 (additional versions can be added)
- **Energy consumption tracking** with automatic kWh calculation
- **Diagnostic sensors** for connection status and error monitoring

## Supported Models

- Hargassner Nano-PK (various firmware versions)
- Other Hargassner models with telnet interface

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add `https://github.com/bauer-group/IP-HargassnerIntegration` and select "Integration" as category
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/bauergroup_hargassnerintegration` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

### Via UI (recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Bauergroup Hargassner**
4. Enter the configuration:
   - **Host/IP**: IP address of your boiler (e.g., `192.168.1.100`)
   - **Firmware Version**: Select your boiler's firmware version
   - **Device Name**: Friendly name for your boiler (default: "Hargassner")
   - **Language**: Choose language for state translations (EN/DE)
   - **Sensor Set**: Standard (basic sensors) or Full (all available sensors)

### Via YAML (not recommended)

```yaml
# configuration.yaml
bauergroup_hargassnerintegration:
  host: 172.16.0.123
  firmware: V14_1HAR_q1
  name: "Hargassner Boiler"
  language: EN
  sensors: FULL
```

## Available Sensors

### Standard Sensor Set

- **Boiler State** - Current operating state (Off, Ignition, Full firing, etc.)
- **Operation Status** - Error/warning notifications
- **Boiler Temperature** - Current boiler temperature (°C)
- **Smoke Gas Temperature** - Exhaust gas temperature (°C)
- **Output** - Current heating power (%)
- **Outside Temperature** - External temperature sensor (°C)
- **Buffer Temperatures** - Multiple buffer tank sensors (°C)
- **Return Temperature** - Heating circuit return (°C)
- **Buffer Level** - Buffer tank fill level (%)
- **Pellet Stock** - Remaining pellets (kg)
- **Pellet Consumption** - Total pellets consumed (kg)
- **Energy Consumption** - Calculated energy usage (kWh)
- **Flow Temperature** - Heating circuit flow (°C)

### Full Sensor Set

Includes all standard sensors plus:
- O2 levels and targets
- Draft pressure
- Motor currents (delivery, grate, cleaning)
- Runtime counters
- Ash removal statistics
- All heating circuits (up to 6)
- Hot water circuits (up to 3)
- Digital I/O states

## Energy Dashboard Integration

The integration automatically creates an energy sensor compatible with Home Assistant's Energy Dashboard:

1. Go to **Settings** → **Dashboards** → **Energy**
2. Add the **Hargassner Energy Consumption** sensor to track your pellet heating energy usage

## Troubleshooting

### Connection Issues

- Ensure telnet (port 23) is enabled on your boiler
- Check firewall settings
- Verify IP address and network connectivity
- Check logs: **Settings** → **System** → **Logs**

### Incorrect Data

- Verify the correct firmware version is selected
- Check encoding in logs
- Enable debug logging (see below)

### Enable Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.bauergroup_hargassnerintegration: debug
```

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed technical documentation.

## Development

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for development guidelines.

## Contributing

Contributions are welcome! Please read [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) first.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Based on the original nano_pk integration, completely rewritten with modern Home Assistant best practices.

## Support

- [Issue Tracker](https://github.com/bauer-group/IP-HargassnerIntegration/issues)
- [Discussions](https://github.com/bauer-group/IP-HargassnerIntegration/discussions)
