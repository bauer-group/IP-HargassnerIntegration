"""Sensor platform for Hargassner Pellet Boiler."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfMass,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    BOILER_STATES_DE,
    BOILER_STATES_EN,
    CONF_DEVICE_NAME,
    CONF_EFFICIENCY,
    CONF_LANGUAGE,
    CONF_PELLET_ENERGY,
    CONF_SENSOR_SET,
    DEFAULT_EFFICIENCY,
    DEFAULT_PELLET_ENERGY,
    DOMAIN,
    ERROR_CODES,
    LANGUAGE_DE,
    SENSOR_SET_FULL,
    STATE_CONNECTED,
    STATE_DISCONNECTED,
)
from .coordinator import HargassnerDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


# Sensor definitions: (key, name, device_class, state_class, icon)
# Note: Keys must match the exact parameter names from the firmware template XML
STANDARD_SENSORS = [
    ("TK", "Kesseltemperatur", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:thermometer"),
    ("TRG", "Rauchgastemperatur", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:smoke"),
    ("Leistung", "Ausgangsleistung", None, SensorStateClass.MEASUREMENT, "mdi:fire"),
    ("Taus", "Außentemperatur", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:thermometer"),
    ("TPo", "Puffer Oben", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:thermometer-lines"),
    ("TPm", "Puffer Mitte", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:thermometer-lines"),
    ("TPu", "Puffer Unten", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:thermometer-lines"),
    ("TB1", "Warmwasser", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:water-boiler"),
    ("TRL", "Rücklauftemperatur", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:coolant-temperature"),
    ("Puff Füllgrad", "Pufferfüllgrad", None, SensorStateClass.MEASUREMENT, "mdi:gauge"),
    ("Lagerstand", "Pelletvorrat", None, SensorStateClass.TOTAL, "mdi:silo"),
    ("Verbrauchszähler", "Pelletverbrauch", None, SensorStateClass.TOTAL_INCREASING, "mdi:counter"),
    ("TVL_1", "Vorlauf Heizkreis 1", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:coolant-temperature"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hargassner sensors from a config entry."""
    coordinator: HargassnerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensor_set = entry.data.get(CONF_SENSOR_SET, "STANDARD")
    language = entry.data.get(CONF_LANGUAGE, "EN")

    entities: list[SensorEntity] = []

    # Always add connection sensor
    entities.append(HargassnerConnectionSensor(coordinator, entry, language))

    # Add boiler state sensor
    entities.append(HargassnerStateSensor(coordinator, entry, language))

    # Add error sensor
    entities.append(HargassnerErrorSensor(coordinator, entry, language))

    # Add energy sensor
    entities.append(HargassnerEnergySensor(coordinator, entry, language))

    # Add sensors based on sensor set configuration
    if sensor_set == SENSOR_SET_FULL:
        # FULL mode: Create sensors for ALL parameters from firmware template
        # Get all parameter names from the message parser
        for param_def in coordinator.telnet_client._parser.parameters:
            param_name = param_def.name

            # Determine device class based on unit
            device_class = None
            if param_def.unit == "°C":
                device_class = SensorDeviceClass.TEMPERATURE
            elif param_def.unit == "mA":
                device_class = SensorDeviceClass.CURRENT
            elif param_def.unit in ["mbar", "bar"]:
                device_class = SensorDeviceClass.PRESSURE

            # Determine state class
            state_class = None
            if not param_def.is_digital:
                # Most analog sensors are measurements
                # Special cases for counters
                if param_name in ["Verbrauchszähler", "Brennerstarts", "Betriebsstunden"]:
                    state_class = SensorStateClass.TOTAL_INCREASING
                elif param_name == "Lagerstand":
                    state_class = SensorStateClass.TOTAL
                else:
                    state_class = SensorStateClass.MEASUREMENT

            # Select language from bilingual description
            desc_dict = param_def.description
            if isinstance(desc_dict, dict):
                display_name = desc_dict.get(language.lower(), desc_dict.get("en", param_name))
            else:
                display_name = desc_dict  # Fallback if it's already a string

            # Create sensor
            entities.append(
                HargassnerParameterSensor(
                    coordinator,
                    entry,
                    param_name,
                    display_name,  # No device prefix - handled by has_entity_name
                    device_class,
                    state_class,
                    None,  # icon
                )
            )
    else:
        # STANDARD mode: Only create predefined sensors
        for sensor_def in STANDARD_SENSORS:
            key, name, device_class, state_class, icon = sensor_def
            entities.append(
                HargassnerParameterSensor(
                    coordinator,
                    entry,
                    key,
                    name,  # No device prefix - handled by has_entity_name
                    device_class,
                    state_class,
                    icon,
                )
            )

    async_add_entities(entities)


class HargassnerBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Hargassner sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: HargassnerDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.data.get(CONF_DEVICE_NAME, "Hargassner Boiler"),
            manufacturer="Hargassner",
            model="Nano-PK",
            sw_version=entry.data.get("firmware", "Unknown"),
            configuration_url=f"http://{entry.data.get('host', '')}",
        )


class HargassnerConnectionSensor(HargassnerBaseSensor):
    """Sensor representing connection status."""

    _attr_icon = "mdi:network-outline"

    def __init__(
        self,
        coordinator: HargassnerDataUpdateCoordinator,
        entry: ConfigEntry,
        language: str,
    ) -> None:
        """Initialize connection sensor."""
        super().__init__(coordinator, entry)
        self._attr_name = "Connection" if language.upper() == "EN" else "Verbindung"
        self._attr_unique_id = f"{entry.entry_id}_connection"
        self._language = language

    @property
    def native_value(self) -> str:
        """Return connection state."""
        if self.coordinator.telnet_client.connected:
            return "Verbunden" if self._language.upper() == "DE" else "Connected"
        return "Getrennt" if self._language.upper() == "DE" else "Disconnected"

    @property
    def icon(self) -> str:
        """Return icon based on connection state."""
        if self.coordinator.telnet_client.connected:
            return "mdi:network-outline"
        return "mdi:network-off-outline"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        stats = self.coordinator.telnet_client.statistics
        return {
            "messages_received": stats.get("messages_received", 0),
            "messages_parsed": stats.get("messages_parsed", 0),
            "parse_errors": stats.get("parse_errors", 0),
            "reconnections": stats.get("reconnections", 0),
            "last_error": stats.get("last_error"),
            "last_update": self.coordinator.telnet_client.last_update,
        }


class HargassnerStateSensor(HargassnerBaseSensor):
    """Sensor for boiler state."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:fireplace"

    def __init__(
        self,
        coordinator: HargassnerDataUpdateCoordinator,
        entry: ConfigEntry,
        language: str,
    ) -> None:
        """Initialize state sensor."""
        super().__init__(coordinator, entry)
        self._attr_name = "Boiler State" if language.upper() == "EN" else "Kesselzustand"
        self._attr_unique_id = f"{entry.entry_id}_state"
        self._language = language
        self._attr_options = BOILER_STATES_DE if language.upper() == "DE" else BOILER_STATES_EN

    @property
    def native_value(self) -> str | None:
        """Return boiler state."""
        zk_data = self.coordinator.data.get("ZK")
        if not zk_data:
            return None

        try:
            state_idx = int(zk_data.get("value", 0))
            if 0 <= state_idx < len(self._attr_options):
                return self._attr_options[state_idx]
        except (ValueError, TypeError):
            pass

        return "Unbekannt" if self._language.upper() == "DE" else "Unknown"

    @property
    def icon(self) -> str:
        """Return icon based on state."""
        zk_data = self.coordinator.data.get("ZK")
        if zk_data:
            try:
                state_idx = int(zk_data.get("value", 0))
                if state_idx in [6, 7]:  # Transition to FF or Full firing
                    return "mdi:fireplace"
            except (ValueError, TypeError):
                pass
        return "mdi:fireplace-off"


class HargassnerErrorSensor(HargassnerBaseSensor):
    """Sensor for error status."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:alert"

    def __init__(
        self,
        coordinator: HargassnerDataUpdateCoordinator,
        entry: ConfigEntry,
        language: str,
    ) -> None:
        """Initialize error sensor."""
        super().__init__(coordinator, entry)
        self._attr_name = "Operation Status" if language.upper() == "EN" else "Betriebsstatus"
        self._attr_unique_id = f"{entry.entry_id}_operation"
        self._language = language
        self._attr_options = ["OK"] + [
            err[language.lower()] for err in ERROR_CODES.values()
        ]

    @property
    def native_value(self) -> str:
        """Return error status."""
        # Get error code from "Störungs Nr" analog parameter
        # 0 = no error, >0 = error code
        error_code_data = self.coordinator.data.get("Störungs Nr")

        if not error_code_data:
            return "OK"

        error_code = str(int(error_code_data.get("value", 0)))

        if error_code == "0":
            return "OK"

        # Error is present - look up description
        error_info = ERROR_CODES.get(error_code)
        if error_info:
            return error_info[self._language.lower()]

        return f"Error {error_code}"

    @property
    def icon(self) -> str:
        """Return icon based on error state."""
        if self.native_value == "OK":
            return "mdi:check"
        return "mdi:alert"


class HargassnerParameterSensor(HargassnerBaseSensor):
    """Sensor for a single boiler parameter."""

    def __init__(
        self,
        coordinator: HargassnerDataUpdateCoordinator,
        entry: ConfigEntry,
        param_key: str,
        name: str,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
        icon: str | None,
    ) -> None:
        """Initialize parameter sensor."""
        super().__init__(coordinator, entry)
        self._param_key = param_key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{param_key}"
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        if icon:
            self._attr_icon = icon

    @property
    def native_value(self) -> float | int | str | None:
        """Return parameter value."""
        param_data = self.coordinator.data.get(self._param_key)
        if param_data:
            return param_data.get("value")
        return None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement."""
        param_data = self.coordinator.data.get(self._param_key)
        if param_data and param_data.get("unit"):
            unit = param_data["unit"]

            # Map units to Home Assistant constants
            if unit == "°C":
                return UnitOfTemperature.CELSIUS
            if unit == "%":
                return PERCENTAGE
            if unit == "kg":
                return UnitOfMass.KILOGRAMS

            return unit
        return None


class HargassnerEnergySensor(HargassnerBaseSensor):
    """Sensor for energy consumption calculated from pellet usage."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_icon = "mdi:radiator"

    def __init__(
        self,
        coordinator: HargassnerDataUpdateCoordinator,
        entry: ConfigEntry,
        language: str,
    ) -> None:
        """Initialize energy sensor."""
        super().__init__(coordinator, entry)
        self._attr_name = "Heat Output" if language.upper() == "EN" else "Wärmemenge"
        self._attr_unique_id = f"{entry.entry_id}_energy"
        self._language = language
        self._entry = entry

    @property
    def native_value(self) -> float | None:
        """Return heat output in kWh (calculated from pellet consumption with efficiency)."""
        pellet_data = self.coordinator.data.get("Verbrauchszähler")
        if pellet_data:
            try:
                pellets_kg = float(pellet_data.get("value", 0))

                # Get configuration values
                pellet_energy = self._entry.data.get(CONF_PELLET_ENERGY, DEFAULT_PELLET_ENERGY)
                efficiency = self._entry.data.get(CONF_EFFICIENCY, DEFAULT_EFFICIENCY)

                # Calculate: kg * kWh/kg * efficiency%
                return pellets_kg * pellet_energy * (efficiency / 100.0)
            except (ValueError, TypeError):
                pass
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        pellet_energy = self._entry.data.get(CONF_PELLET_ENERGY, DEFAULT_PELLET_ENERGY)
        efficiency = self._entry.data.get(CONF_EFFICIENCY, DEFAULT_EFFICIENCY)

        return {
            "pellet_energy_kwh_per_kg": pellet_energy,
            "efficiency_percent": efficiency,
            "calculation": f"{pellet_energy} kWh/kg × {efficiency}% efficiency",
        }
