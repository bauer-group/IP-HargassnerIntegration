# Architecture Documentation

## Overview

The Hargassner Pellet Boiler integration is built using modern Home Assistant best practices with a focus on reliability, maintainability, and thread-safety.

## Component Structure

```
hargassner_pellet/
├── __init__.py                 # Integration entry point
├── config_flow.py             # GUI configuration flow
├── const.py                   # Constants and configuration
├── coordinator.py             # Data update coordinator
├── manifest.json              # Integration metadata
├── sensor.py                  # Sensor platform implementation
├── src/                       # Core business logic
│   ├── __init__.py
│   ├── firmware_templates.py  # Firmware version definitions
│   ├── message_parser.py      # Telnet message parser
│   └── telnet_client.py       # Thread-safe telnet client
└── translations/              # Localization files
    ├── en.json
    └── de.json
```

## Architecture Layers

### 1. Integration Layer (`__init__.py`)

**Responsibilities:**
- Setup and teardown of the integration
- Creation of telnet client and coordinator
- Platform registration

**Key Functions:**
- `async_setup_entry()` - Initialize integration from config entry
- `async_unload_entry()` - Cleanup when integration is removed
- `async_reload_entry()` - Reload integration on configuration changes

### 2. Configuration Layer (`config_flow.py`)

**Responsibilities:**
- User interface for integration setup
- Connection validation
- Options flow for runtime configuration changes

**Features:**
- GUI-based configuration (Config Flow)
- Connection testing before entry creation
- Unique ID validation (one entry per boiler IP)
- Options flow for changing language and sensor set

### 3. Data Coordination Layer (`coordinator.py`)

**Responsibilities:**
- Bridge between telnet client and Home Assistant
- Periodic data refresh scheduling
- Error handling and recovery

**Key Features:**
- Extends `DataUpdateCoordinator` for standardized data management
- 5-second update interval (configurable via `UPDATE_INTERVAL`)
- Automatic retry on failure
- Thread-safe data access

### 4. Telnet Client Layer (`src/telnet_client.py`)

**Responsibilities:**
- Persistent telnet connection management
- Background message receiving
- Automatic reconnection with exponential backoff
- Thread-safe data storage

**Architecture:**

```
┌─────────────────────────────────────┐
│   HargassnerTelnetClient            │
├─────────────────────────────────────┤
│  Connection Management:             │
│  - async_start()                    │
│  - async_stop()                     │
│  - _connect()                       │
│  - _close_connection()              │
├─────────────────────────────────────┤
│  Background Tasks:                  │
│  - _receiver_loop()                 │
│    └─ Continuous message receiving  │
│  - _process_data()                  │
│    └─ Encoding detection & parsing  │
├─────────────────────────────────────┤
│  Data Access:                       │
│  - get_latest_data() [async lock]   │
│  - register_callback()              │
│  - unregister_callback()            │
└─────────────────────────────────────┘
```

**Key Features:**

1. **Automatic Reconnection:**
   - Exponential backoff: 5s → 10s → 20s → ... → 300s (max)
   - Resets to 5s on successful receive
   - Continues indefinitely while `_running` is True

2. **Encoding Handling:**
   - Tries UTF-8, Latin-1, CP1252 in sequence
   - Fallback to UTF-8 with character replacement
   - Ensures °C symbols are correctly decoded

3. **Thread Safety:**
   - `asyncio.Lock` protects `_latest_data`
   - All data access is async-safe
   - Callbacks executed in asyncio context

4. **Statistics Tracking:**
   - Messages received/parsed counters
   - Parse error tracking
   - Reconnection count
   - Last error message

### 5. Message Parser Layer (`src/message_parser.py`)

**Responsibilities:**
- Parse XML firmware templates
- Extract values from telnet messages
- Type conversion and validation

**Architecture:**

```
┌──────────────────────────────────────┐
│   HargassnerMessageParser            │
├──────────────────────────────────────┤
│  Initialization:                     │
│  - _parse_template()                 │
│    └─ Build ParameterDefinition map  │
├──────────────────────────────────────┤
│  Message Processing:                 │
│  - parse_message(line)               │
│    ├─ Split "pm <v1> <v2> ..."       │
│    ├─ Validate length                │
│    └─ Extract all parameters         │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│   ParameterDefinition                │
├──────────────────────────────────────┤
│  Attributes:                         │
│  - name: Parameter identifier        │
│  - index: Position in message        │
│  - unit: Measurement unit            │
│  - is_digital: Boolean flag          │
│  - bit_mask: For digital parameters  │
├──────────────────────────────────────┤
│  Methods:                            │
│  - parse_value(values)               │
│    ├─ Extract from array             │
│    ├─ Type conversion                │
│    └─ Bit extraction for digital     │
└──────────────────────────────────────┘
```

**Key Features:**

1. **XML Template Parsing:**
   - Supports `<ANALOG>` channels (numeric values)
   - Supports `<DIGITAL>` channels (bitfields)
   - Automatic calculation of expected message length

2. **Flexible Parsing:**
   - Logs warning if message length differs (doesn't fail)
   - Continues parsing available data
   - Returns `None` for missing/invalid values

3. **Type Handling:**
   - Analog: `float` (if decimal point) or `int`
   - Digital: `bool` (bit extraction)
   - Graceful error handling on parse failure

### 6. Firmware Templates (`src/firmware_templates.py`)

**Responsibilities:**
- Define message structure for each firmware version
- Provide parameter descriptions

**Supported Versions:**
- `V14_1HAR_q1` - 112 analog + many digital parameters
- Additional versions can be added easily

**Template Format:**
```xml
<DAQPRJ>
  <ANALOG>
    <CHANNEL id='0' name='ZK' unit=''/>
    <CHANNEL id='1' name='O2' unit='%'/>
    ...
  </ANALOG>
  <DIGITAL>
    <CHANNEL id='0' bit='0' name='Störung'/>
    ...
  </DIGITAL>
</DAQPRJ>
```

### 7. Sensor Platform (`sensor.py`)

**Responsibilities:**
- Create Home Assistant sensor entities
- Map boiler parameters to sensor types
- Provide device info and attributes

**Sensor Types:**

1. **HargassnerConnectionSensor**
   - State: `connected` / `disconnected`
   - Attributes: Statistics, last update, errors
   - Icon: Dynamic based on connection state

2. **HargassnerStateSensor**
   - State: Boiler operating state (enum)
   - Options: Language-specific state names
   - Icon: `fireplace` when firing, `fireplace-off` otherwise

3. **HargassnerErrorSensor**
   - State: Error message or "OK"
   - Options: Language-specific error descriptions
   - Icon: `check` when OK, `alert` on error

4. **HargassnerParameterSensor**
   - Generic sensor for any parameter
   - Automatic unit mapping (°C → UnitOfTemperature.CELSIUS)
   - Device class and state class configuration

5. **HargassnerEnergySensor** (Wärmemenge)
   - Calculates heat output from pellet consumption
   - Formula: `kg * pellet_energy_kwh_per_kg * (efficiency_percent / 100)`
   - Configurable pellet energy (default: 4.8 kWh/kg)
   - Configurable efficiency (default: 90%)
   - Example: 100 kg * 4.8 kWh/kg * 0.90 = 432 kWh
   - Energy dashboard compatible
   - Attributes show calculation parameters

**Sensor Sets:**

- **STANDARD**: 13 essential sensors (temperatures, output, stock, etc.)
- **FULL**: All available parameters (30+ sensors depending on firmware)

## Data Flow

```
┌─────────────┐
│   Boiler    │
│  (Telnet)   │
└──────┬──────┘
       │ "pm 7 10.1 9.0 67.4 ..."
       ↓
┌──────────────────────┐
│  TelnetClient        │
│  _receiver_loop()    │
├──────────────────────┤
│  - Receive raw bytes │
│  - Decode (UTF-8/...)│
│  - Extract lines     │
└──────┬───────────────┘
       │ Decoded string
       ↓
┌──────────────────────┐
│  MessageParser       │
│  parse_message()     │
├──────────────────────┤
│  - Split values      │
│  - Map to parameters │
│  - Type conversion   │
└──────┬───────────────┘
       │ {TK: {value: 67.4, unit: "°C"}, ...}
       ↓
┌──────────────────────┐
│  TelnetClient        │
│  _latest_data        │
│  (async locked)      │
└──────┬───────────────┘
       │ Periodic poll (5s)
       ↓
┌──────────────────────┐
│  Coordinator         │
│  _async_update_data()│
└──────┬───────────────┘
       │ Data update event
       ↓
┌──────────────────────┐
│  Sensor Entities     │
│  - ConnectionSensor  │
│  - StateSensor       │
│  - ParameterSensors  │
│  - EnergySensor      │
└──────────────────────┘
```

## Error Handling Strategy

### Connection Errors

1. **Initial Connection Failure:**
   - Raises `ConfigEntryNotReady`
   - Home Assistant will retry automatically

2. **Runtime Connection Loss:**
   - Background task continues reconnecting
   - Coordinator marks data as unavailable
   - Sensors show "unavailable" state

3. **Exponential Backoff:**
   - Prevents rapid reconnection attempts
   - Reduces load on boiler's telnet server

### Parsing Errors

1. **Invalid Encoding:**
   - Try multiple encodings
   - Fallback to replacement characters
   - Log warning but continue

2. **Message Length Mismatch:**
   - Log warning
   - Parse available data
   - Don't fail completely

3. **Invalid Values:**
   - Return `None` for parameter
   - Sensor shows "unknown"
   - Continue parsing other parameters

### Update Errors

1. **No Data Available:**
   - Return empty dict (not an error on startup)
   - Log debug message

2. **Update Timeout:**
   - Coordinator retries automatically
   - Exponential backoff built into coordinator

## Thread Safety

### Async Context

All components use `asyncio` for concurrency:
- No threads (only async tasks)
- Event loop ensures sequential execution
- `asyncio.Lock` for shared data

### Shared Data Access

**TelnetClient `_latest_data`:**
```python
async with self._data_lock:
    self._latest_data = parsed_data
```

**Coordinator Data Access:**
```python
async def get_latest_data(self) -> dict:
    async with self._data_lock:
        return self._latest_data.copy()
```

### Callback Safety

Callbacks are executed in asyncio context:
- Exceptions are caught and logged
- Failing callback doesn't affect others
- No blocking operations allowed

## Configuration

### Config Entry Data

```python
{
    "host": "192.168.1.100",           # Required
    "firmware": "V14_1HAR_q1",         # Required
    "device_name": "Hargassner",       # Optional
    "language": "EN",                  # Optional
    "sensor_set": "STANDARD",          # Optional
}
```

### Options

Users can change at runtime:
- `language` - Switch between EN/DE
- `sensor_set` - Switch between STANDARD/FULL

Requires integration reload to apply.

## Performance Considerations

1. **Update Interval:** 5 seconds
   - Balances responsiveness vs. load
   - Configurable via `UPDATE_INTERVAL`

2. **Message Processing:**
   - Only latest message is used (older discarded)
   - Prevents backlog on slow systems

3. **Data Copying:**
   - `get_latest_data()` returns copy (not reference)
   - Prevents race conditions
   - Minimal overhead (dict copy is fast)

4. **Sensor Creation:**
   - Only requested sensors are created
   - STANDARD mode: ~15 entities
   - FULL mode: ~30-50 entities (firmware dependent)

## Extensibility

### Adding New Firmware Versions

1. Add XML template to `firmware_templates.py`
2. Add version to `FIRMWARE_VERSIONS` in `const.py`
3. No code changes needed - parser handles automatically

### Adding Custom Sensors

1. Define in `STANDARD_SENSORS` or `ADDITIONAL_SENSORS`
2. Specify device class, state class, and icon
3. Sensor automatically created if parameter exists

### Adding New Platforms

Follow Home Assistant platform pattern:
- `binary_sensor.py` - For on/off states
- `switch.py` - For controllable outputs (future)
- `climate.py` - For temperature control (future)

## Testing Recommendations

1. **Connection Testing:**
   - Test with invalid IP (should fail gracefully)
   - Test with unreachable IP (timeout)
   - Test reconnection after network outage

2. **Message Parsing:**
   - Test with actual boiler messages
   - Test with truncated messages
   - Test with extra values

3. **Encoding:**
   - Test with UTF-8 messages
   - Test with Latin-1 (umlauts, degree symbols)
   - Test with corrupted data

4. **Integration:**
   - Test reload
   - Test removal
   - Test Home Assistant restart

## Security Considerations

1. **No Authentication:**
   - Telnet is unencrypted and unauthenticated
   - Should only be used on trusted networks
   - Consider VPN for remote access

2. **Input Validation:**
   - All telnet data is parsed defensively
   - Type conversion has error handling
   - No code execution from messages

3. **Resource Limits:**
   - Buffer size limited to 64KB
   - Message length validated
   - Timeout prevents hanging

## Future Enhancements

1. **Write Support:**
   - Send commands to boiler (if protocol allows)
   - Control heating circuits
   - Adjust temperatures

2. **Historical Data:**
   - Store parameter history
   - Calculate statistics (avg, min, max)
   - Pellet consumption trends

3. **Advanced Features:**
   - Predictive maintenance alerts
   - Efficiency calculations
   - Integration with weather forecast

4. **Protocol Documentation:**
   - Reverse engineer full telnet protocol
   - Document all commands
   - Create protocol specification
