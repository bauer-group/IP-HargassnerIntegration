<div align="center">
  <img src="custom_components/bauergroup_hargassnerintegration/icon.png" alt="Hargassner Integration Logo" width="200"/>

  # Hargassner Pellet Boiler Integration
  ### for Home Assistant

  [![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-blue?style=for-the-badge&logo=home-assistant)](https://www.home-assistant.io/)

  [![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
  [![License](https://img.shields.io/github/license/bauer-group/IP-HargassnerIntegration?style=for-the-badge)](LICENSE)

  [![GitHub Release](https://img.shields.io/github/v/release/bauer-group/IP-HargassnerIntegration?style=for-the-badge)](https://github.com/bauer-group/IP-HargassnerIntegration/releases)
  [![GitHub Issues](https://img.shields.io/github/issues/bauer-group/IP-HargassnerIntegration?style=for-the-badge)](https://github.com/bauer-group/IP-HargassnerIntegration/issues)
  [![GitHub Stars](https://img.shields.io/github/stars/bauer-group/IP-HargassnerIntegration?style=for-the-badge)](https://github.com/bauer-group/IP-HargassnerIntegration/stargazers)

  **Modern, professional Home Assistant integration for Hargassner pellet boilers with real-time telnet monitoring.**

  [Features](#-features) • [Screenshots](#-screenshots) • [Installation](#-installation) • [Configuration](#️-configuration) • [Documentation](#-documentation) • [Support](#support)
</div>

---

## ✨ Features

- 🔥 **Real-time monitoring** of 228 boiler parameters via direct connection
- 🔄 **Automatic reconnection** with exponential backoff strategy
- 🔒 **Thread-safe** async telnet client with background processing
- 🛡️ **Robust error handling** with custom exception types
- 🎛️ **GUI configuration** via Home Assistant Config Flow
- 🔧 **Firmware support** for V14_1HAR_q1 (extensible architecture)
- ⚡ **Energy Dashboard** integration with automatic kWh calculation
- 🌍 **Bilingual** sensor names and states (EN/DE)
- 📊 **Flexible sensor sets**: Standard (17 sensors) or Full (228 sensors)
- 🔌 **Local polling** - no cloud dependency

## 📸 Screenshots

<div align="center">

### Device Overview
<img src="docs/images/Device_Example.png" alt="Device Overview" width="800"/>

### Sensor Dashboard
<img src="docs/images/Dashboard_Example.png" alt="Dashboard Example" width="800"/>

### Detailed Sensor View
<img src="docs/images/Device_Detail_Example.png" alt="Device Detail" width="800"/>

### Energy Dashboard Integration

<img src="docs/images/Energy_Dashboard_Example.png" alt="Energy Dashboard" width="800"/>

### Custom Dashboard with Pellet Consumption Forecast

<img src="docs/images/Custom_Dashboard.png" alt="Custom Dashboard" width="800"/>

</div>

## 🔥 Supported Models

| Model | Firmware | Status |
|-------|----------|--------|
| Nano-PK | V14_1HAR_q1 | ✅ Fully tested |
| Nano-PK | V14_1HAR_q1 |  tested - use at own risk |
| Other Hargassner models | Custom | ⚠️ Requires firmware template |

> **Note:** Additional firmware versions can be easily added via XML templates. See [Adding Firmware Support](docs/ADDING_FIRMWARE.md) (EN) or [Neue Firmware hinzufügen](docs/ADDING_FIRMWARE_DE.md) (DE) for details.

## 📦 Installation

### Method 1: HACS (Recommended)

1. Open **HACS** in Home Assistant
2. Go to **Integrations**
3. Click the **⋮** menu → **Custom repositories**
4. Add repository:
   - **URL:** `https://github.com/bauer-group/IP-HargassnerIntegration`
   - **Category:** Integration
5. Click **Install**
6. **Restart Home Assistant**

### Method 2: Manual Installation

```bash
cd /config
git clone https://github.com/bauer-group/IP-HargassnerIntegration.git
cp -r IP-HargassnerIntegration/custom_components/bauergroup_hargassnerintegration custom_components/
```

Then restart Home Assistant.

## ⚙️ Configuration

### Quick Start

1. **Settings** → **Devices & Services** → **Add Integration**
2. Search for **"Bauergroup Hargassner"**
3. Configure:

| Field | Description | Example |
|-------|-------------|---------|
| **Host** | IP address of boiler | `192.168.1.100` |
| **Firmware** | Boiler firmware version | `V14_1HAR_q1` |
| **Device Name** | Friendly name | `Hargassner` |
| **Language** | UI language (EN/DE) | `DE` |
| **Sensor Set** | STANDARD or FULL | `FULL` |
| **Pellet Energy** | Energy content (kWh/kg) | `4.8` (default) |
| **Efficiency** | Boiler efficiency (%) | `90` (default) |

### Sensor Sets Comparison

| Set | Sensors | Use Case |
|-----|---------|----------|
| **STANDARD** | 17 sensors | Basic monitoring, dashboards |
| **FULL** | 228 sensors | Advanced diagnostics, all parameters |

> 💡 **Tip:** Start with STANDARD, switch to FULL if you need detailed diagnostics.

## 📊 Available Sensors

### STANDARD Set (17 Sensors)

**Always Available (4):**

- 🔌 **Connection** - Connected/Disconnected
- 🔥 **Boiler State** - Off, Ignition, Full Firing, etc.
- ⚠️ **Operation Status** - OK / Error messages
- ⚡ **Heat Output** (Wärmemenge) - kWh (calculated from pellet consumption with configurable efficiency)

**Core Parameters (13):**

- 🌡️ **Boiler Temperature** (TK)
- 💨 **Flue Gas Temperature** (TRG)
- 📈 **Output Power** (%)
- 🌍 **Outside Temperature**
- 🔵 **Buffer Top/Middle/Bottom** (3 sensors)
- 💧 **Hot Water Temperature** (TB1)
- ↩️ **Return Temperature** (TRL)
- 📊 **Buffer Fill Level** (%)
- 🪵 **Pellet Stock** (kg)
- 📉 **Pellet Consumption** (kg)
- ➡️ **Flow Temperature HC1** (TVL_1)

### FULL Set (228 Sensors)

All STANDARD sensors **plus** 211 additional parameters:

**Analog Sensors (112):**

- All temperatures (Boiler, Buffer, HC 1-8, DHW, Solar)
- O2 levels, Lambda values, Draft pressure
- All valve positions (HC 1-8)
- Motor currents (delivery, grate, ash removal)
- Pellet stock, consumption, ash content
- System time (minute, hour, day, month, year)
- Analog inputs (AN11-AN16)

**Digital Sensors (112):**

- Motors (M1-M38): Pumps, mixers, feeders, ash removal
- Inputs (E1-E16): Switches, thermostats, errors
- Heating circuit modes (HC1-HC8): Auto, Party, Holiday
- Operating modes: Auto, Manual, Heating, Error
- Time programs: Reduced, Normal, Party countdown

## Energy Dashboard Integration

The integration automatically creates a heat output sensor compatible with Home Assistant's Energy Dashboard:

1. Go to **Settings** → **Dashboards** → **Energy**
2. Add the **Hargassner Heat Output** (Wärmemenge) sensor to track your pellet heating energy usage

### Customizing Energy Calculation

The heat output is calculated using the formula:

```
Heat (kWh) = Pellets (kg) × Energy Content (kWh/kg) × Efficiency (%)
```

You can customize both values in the integration options:

- **Pellet Energy Content**: Default 4.8 kWh/kg (range: 3.0-6.0)
- **Boiler Efficiency**: Default 90% (range: 50-100%)

**Example**: With 100 kg pellets consumed, 4.8 kWh/kg energy content, and 90% efficiency:
```
100 kg × 4.8 kWh/kg × 0.90 = 432 kWh
```

To adjust these values:
1. Go to **Settings** → **Devices & Services**
2. Find your Hargassner integration
3. Click **Configure** → Adjust values as needed

## 📚 Documentation

### User Guides

- **[Quick Start Guide](README.md#️-configuration)** - Get started in 5 minutes
- **[German Quick Start (SCHNELLSTART.md)](SCHNELLSTART.md)** - Schnellstartanleitung auf Deutsch
- **[Detailed Installation Guide](docs/INSTALLATION.md)** - Step-by-step installation instructions
- **[Energy Dashboard Setup](README.md#energy-dashboard-integration)** - Configure energy tracking
- **[Custom Dashboard Setup](docs/CUSTOM_DASHBOARD.md)** - Complete dashboard with consumption forecasts and HDD analysis

### Technical Documentation

- **[Architecture Overview](docs/ARCHITECTURE.md)** - Deep-dive into technical architecture, data flow, and design decisions
- **[Development Guide](docs/DEVELOPMENT.md)** - Developer setup, coding standards, and workflow
- **[Adding Firmware Support](docs/ADDING_FIRMWARE.md)** - Guide for adding new firmware versions (English)
- **[Neue Firmware hinzufügen](docs/ADDING_FIRMWARE_DE.md)** - Anleitung für neue Firmware-Versionen (Deutsch)
- **[Contributing Guidelines](docs/CONTRIBUTING.md)** - How to contribute to this project

### Troubleshooting

- **[Common Issues](README.md#troubleshooting)** - Solutions for connection and data problems
- **[Debug Logging](README.md#enable-debug-logging)** - Enable detailed logging for diagnosis

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

## Support

- [Issue Tracker](https://github.com/bauer-group/IP-HargassnerIntegration/issues)
- [Discussions](https://github.com/bauer-group/IP-HargassnerIntegration/discussions)
