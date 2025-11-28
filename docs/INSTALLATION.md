# Installation Guide

## Requirements

- Home Assistant 2024.1 or later
- Hargassner pellet boiler with telnet interface
- Network connectivity between Home Assistant and boiler

## Installation Methods

### Method 1: HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=bauer-group&repository=IP-HargassnerIntegration&category=integration)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the 3 dots in the top right corner
4. Select "Custom repositories"
5. Add repository URL: `https://github.com/bauer-group/IP-HargassnerIntegration`
6. Select category: "Integration"
7. Click "Add"
8. Click "Install" on the Hargassner Pellet card
9. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from GitHub
2. Extract the archive
3. Copy `custom_components/bauergroup_hargassnerintegration` to your Home Assistant's `custom_components` directory:
   ```
   <config_dir>/custom_components/bauergroup_hargassnerintegration/
   ```
4. Restart Home Assistant

### Verify Installation

Check Home Assistant logs for:
```
INFO (MainThread) [homeassistant.setup] Setting up bauergroup_hargassnerintegration
```

## Configuration

### Step 1: Enable Telnet on Boiler

Consult your boiler's manual to enable the telnet interface (usually port 23).

**Note:** Telnet is unencrypted. Only use on trusted networks!

### Step 2: Get Boiler IP Address

Find your boiler's IP address:
- Check boiler display/menu
- Check router's DHCP client list
- Use network scanner

**Tip:** Configure a static IP or DHCP reservation for stability.

### Step 3: Test Connection

From any computer on the same network:
```bash
telnet <boiler-ip> 23
```

You should see messages like:
```
pm 7 10.1 9.0 67.4 70 64.5 65 11 91.3 26 27.0 ...
```

Press Ctrl+C to exit.

### Step 4: Add Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **BAUERGROUP Hargassner Integration**
4. Fill in the configuration form:

   - **IP Address:** Enter boiler's IP (e.g., `192.168.1.100`)
   - **Firmware Version:** Select your boiler's version
     - Check boiler display or manual
     - If unsure, try `V14_1HAR_q1` (most common)
   - **Device Name:** Choose a friendly name (default: "Hargassner")
   - **Language:** Select EN (English) or DE (German)
   - **Sensor Set:**
     - **STANDARD** - 16 essential sensors (temperatures, output, stock, etc.)
     - **FULL** - All available sensors from firmware template (varies by version)

5. Click **Submit**

The integration will test the connection. If successful, sensors will be created.

### Step 5: Verify Sensors

1. Go to **Settings** → **Devices & Services**
2. Click on **BAUERGROUP Hargassner Integration**
3. Check that sensors are populated with data

## Troubleshooting

### Connection Failed

**Problem:** "Failed to connect to boiler"

**Solutions:**
1. Verify IP address is correct
2. Check telnet is enabled on boiler
3. Test with `telnet <ip> 23` from command line
4. Check firewall settings
5. Verify Home Assistant and boiler are on same network/VLAN

### No Data / Sensors Show Unknown

**Problem:** Sensors are created but show "Unknown"

**Solutions:**
1. Wait 10-20 seconds for initial data
2. Check Home Assistant logs:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.bauergroup_hargassnerintegration: debug
   ```
3. Verify firmware version is correct
4. Check for parsing errors in logs

### Wrong Firmware Version Selected

**Problem:** Sensors show incorrect values or parsing errors

**Solutions:**
1. Remove integration
2. Re-add with different firmware version
3. Check boiler manual for correct version
4. Enable debug logging to see message format

### Encoding Issues (Special Characters)

**Problem:** Degree symbols (°) show as � or other characters

**Solutions:**
1. Check logs for encoding warnings
2. Integration automatically tries UTF-8, Latin-1, CP1252
3. If problem persists, create GitHub issue with sample messages

### Connection Drops Frequently

**Problem:** Integration keeps disconnecting

**Solutions:**
1. Check network stability
2. Verify no other devices are using telnet to boiler
3. Check boiler doesn't have telnet timeout configured
4. Review logs for specific error messages

## Advanced Configuration

### Changing Options

You can change language and sensor set without removing the integration:

1. Go to **Settings** → **Devices & Services**
2. Click **Configure** on BAUERGROUP Hargassner Integration
3. Change settings
4. Click **Submit**
5. Reload integration or restart Home Assistant

### Multiple Boilers

To add multiple boilers:
1. Each boiler needs a unique IP address
2. Add integration separately for each
3. Use different device names to distinguish them

### Energy Dashboard Integration

The integration automatically creates an energy sensor compatible with HA's Energy Dashboard:

1. Go to **Settings** → **Dashboards** → **Energy**
2. Click **Add Consumption**
3. Select the **Heat Output** (Wärmemenge) sensor
4. Configure as needed

## Firewall Configuration

### Home Assistant Firewall

Allow outbound connections to boiler:
- **Protocol:** TCP
- **Port:** 23
- **Destination:** Boiler IP

### Network Firewall

If boiler is on different subnet:
- Allow TCP port 23 from HA to boiler

## Upgrading

### Via HACS

1. HACS will notify of updates
2. Click **Update**
3. Restart Home Assistant

### Manual Upgrade

1. Download new release
2. Replace `custom_components/bauergroup_hargassnerintegration` folder
3. Restart Home Assistant

**Note:** Check release notes for breaking changes!

## Uninstalling

1. Go to **Settings** → **Devices & Services**
2. Click **...** on BAUERGROUP Hargassner Integration
3. Select **Delete**
4. Confirm deletion
5. (Optional) Remove folder:
   ```
   custom_components/bauergroup_hargassnerintegration/
   ```
6. Restart Home Assistant

## Data Privacy

This integration:
- Communicates directly with your boiler (local network)
- Does NOT send data to cloud services
- Does NOT phone home
- All data stays in your Home Assistant instance

## Support

- **Issues:** https://github.com/bauer-group/IP-HargassnerIntegration/issues
- **Discussions:** https://github.com/bauer-group/IP-HargassnerIntegration/discussions
- **Documentation:** https://github.com/bauer-group/IP-HargassnerIntegration/blob/main/README.md
