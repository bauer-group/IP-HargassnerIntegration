# Adding New Firmware Version Support

This guide explains how to add support for additional Hargassner firmware versions to the integration using the automated DAQ parser tool.

## Table of Contents

- [Overview](#overview)
- [Quick Start (4 Steps)](#quick-start-4-steps)
- [Step 1: Read Firmware Version](#step-1-read-firmware-version)
- [Step 2: Enable SD Card Logging](#step-2-enable-sd-card-logging)
- [Step 3: Parse DAQ File](#step-3-parse-daq-file)
- [Step 4: Insert Code](#step-4-insert-code)
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

1. **Read firmware version from boiler display** (1 min)
2. **Enable SD card logging for a few minutes** (5 min)
3. **Parse DAQ file with tool and generate Python code** (2 min)
4. **Insert Python code in the right places** (2 min)

Done! ✨

---

## Step 1: Read Firmware Version

### On Boiler Display

1. Go to the main menu of your Hargassner boiler
2. Navigate to **Service** or **Info**
3. Look for **Software Version** or **Firmware**
4. Note down the version (e.g., `V14.1HAR.q1`, `V15.2HAR`, etc.)

**Example:**
```
Software: V14.1HAR.q1
Hardware: V1.0
```

You'll need this version later for naming in the code.

---

## Step 2: Enable SD Card Logging

### 2.1 Insert SD Card

If there's no SD card in the boiler yet:

- Open the boiler control panel
- Insert an SD card (usually behind a small door)
- The boiler will start logging automatically

### 2.2 Let Logging Run

**Important:** Let the boiler run for at least **5-10 minutes** with the SD card inserted.

The boiler continuously writes DAQ files with all parameter definitions and measurements.

### 2.3 Remove SD Card

After 5-10 minutes:

- Open the control panel
- Remove the SD card
- Insert it into your computer (SD card reader)

**Note:** The boiler can continue running without the SD card, but won't log new data.

---

## Step 3: Parse DAQ File

### 3.1 Find DAQ File

On the SD card you'll find files like:

```
DAQ00000.DAQ
DAQ00001.DAQ
DAQ00002.DAQ
```

**Which file?** Take the **newest** DAQ file (highest number or latest date).

Typical file size: 1-10 MB

### 3.2 Run DAQ Parser

Open a terminal/command prompt and navigate to the integration's `tools` folder:

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

**Note:** Replace the path to the DAQ file with the actual path on your system (e.g., `E:\DAQ00000.DAQ` if the SD card is mounted as drive E:).

### 3.3 Generated Code

The tool automatically creates a `firmware_template.txt` file with ready-to-use Python code:

**Example Output:**

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
    <!-- ... all other parameters ... -->
  </ANALOG>
  <DIGITAL>
    <CHANNEL id="102" bit="0" name="M1_Kessel_Geblaese" />
    <!-- ... all other bits ... -->
  </DIGITAL>
</DAQPRJ>"""

# Add to FIRMWARE_VERSIONS in const.py
FIRMWARE_VERSIONS.append("V14_1HAR_q1")
```

This code contains:

- ✅ Complete DAQPRJ XML template with all parameters
- ✅ System information (manufacturer, model, version)
- ✅ Statistics (parameter count, message length)
- ✅ Ready-to-use code snippets

---

## Step 4: Insert Code

Now insert the generated code in two places:

### 4.1 File 1: firmware_templates.py

Open: `custom_components/bauergroup_hargassnerintegration/src/firmware_templates.py`

**What to insert:** The complete line with `FIRMWARE_TEMPLATES["..."] = """<DAQPRJ>...</DAQPRJ>"""`

**Where to insert:** In the `FIRMWARE_TEMPLATES` dictionary, below the existing entries.

**Example:**

```python
FIRMWARE_TEMPLATES = {
    # Existing firmware
    "V14_1HAR_q1": """<DAQPRJ>
        <!-- existing template -->
    </DAQPRJ>""",

    # Your new firmware (copy from firmware_template.txt)
    "V15_2HAR": """<DAQPRJ>
        <!-- INSERT COMPLETE DAQPRJ BLOCK HERE -->
    </DAQPRJ>""",
}
```

**Tip:** Simply copy the complete line from `firmware_template.txt` and insert it before the closing `}`.

### 4.2 File 2: const.py

Open: `custom_components/bauergroup_hargassnerintegration/const.py`

**What to insert:** The firmware version as a string

**Where to insert:** In the `FIRMWARE_VERSIONS` list

**Example:**

```python
FIRMWARE_VERSIONS: Final = [
    "V14_1HAR_q1",
    "V15_2HAR",      # Add your new version here
]
```

**Important:** The name must be **exactly identical** to the dictionary key in `firmware_templates.py`!

### 4.3 Done!

That's it! You've successfully:

- ✅ Inserted DAQPRJ XML template into `firmware_templates.py`
- ✅ Added firmware version to `const.py`

Now you can test the integration.

---

## Testing and Validation

After inserting the code, you must test the integration.

### 5.1 Restart Home Assistant

```bash
# Via Home Assistant UI
Settings → System → Restart
```

### 5.2 Enable Debug Logging (Optional)

Add to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.bauergroup_hargassnerintegration: debug
```

Restart Home Assistant again.

### 5.3 Add Integration with New Firmware

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **"Bauergroup Hargassner"**
4. Configure:
   - **Host:** Your boiler's IP address
   - **Firmware:** Select your new firmware version
   - **Sensor Set:** Start with **STANDARD**
5. Click **Submit**

### 5.4 Verify Sensors

Check that sensors are showing correct values:

1. **Settings → Devices & Services → Your Integration**
2. Click on the integration to see all entities
3. Compare sensor values with boiler display:
   - Boiler temperature should match
   - Outside temperature should match
   - Boiler state should match
   - Values should update every 5 seconds

### 5.5 Check Logs

**Settings → System → Logs**

Expected messages:

- ✅ `Successfully connected to boiler`
- ✅ `Parsed message with X parameters`
- ❌ No parsing errors or "Unknown state" warnings

**Example Logs:**

```
[custom_components.bauergroup_hargassnerintegration.src.telnet_client] Successfully connected to 192.168.1.100:23
[custom_components.bauergroup_hargassnerintegration.src.message_parser] Parsed message with 138 values
[custom_components.bauergroup_hargassnerintegration.coordinator] Data update successful
```

### 5.6 Validate with Tools (Optional)

Check template consistency:

```bash
cd tools
python parameter_validator.py
```

The tool checks:

- XML is valid
- No duplicate parameters
- Naming conventions followed
- All standard parameters present

### 5.7 Extended Testing

Let the integration run for 24 hours to ensure:

- Connection remains stable
- No memory leaks
- All sensor values update correctly
- No unexpected errors in logs

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

- Ensure the dictionary key in `FIRMWARE_TEMPLATES` exactly matches the string in `FIRMWARE_VERSIONS`
- Version names are case-sensitive

### Issue: Sensors show "Unknown" state

**Cause:** Parameter not found in telnet message

**Solution:**

- Enable debug logging
- Check logs for message length: `Parsed message with X values`
- Verify the DAQ file is from the same boiler you're connecting to
- Some parameters may not be available on all configurations

### Issue: Wrong sensor values

**Cause:** Parameter index mismatch or wrong firmware template

**Solution:**

- Double-check you're using the correct firmware version in config
- Verify the DAQ file matches your boiler model and firmware
- Compare a few key values manually:
  - Boiler temperature is usually index 3 in most firmwares
  - Outside temperature is typically index 20
  - Check against boiler display to validate

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
- No trailing comma after last entry

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
