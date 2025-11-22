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
    CONF_LANGUAGE,
    CONF_SENSOR_SET,
    DOMAIN,
    ERROR_CODES,
    LANGUAGE_DE,
    PELLET_ENERGY_FACTOR,
    SENSOR_SET_FULL,
    STATE_CONNECTED,
    STATE_DISCONNECTED,
)
from .coordinator import HargassnerDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


# Sensor definitions: (key, name, device_class, state_class, icon)
STANDARD_SENSORS = [
    ("TK", "Boiler Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None),
    ("TRG", "Smoke Gas Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None),
    ("Leistung", "Output Power", None, SensorStateClass.MEASUREMENT, "mdi:fire"),
    ("Taus", "Outside Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None),
    ("TPo", "Buffer Temperature Top", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:thermometer-lines"),
    ("TPm", "Buffer Temperature Middle", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:thermometer-lines"),
    ("TPu", "Buffer Temperature Bottom", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:thermometer-lines"),
    ("TB1", "Hot Water 1 Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:thermometer-lines"),
    ("TRL", "Return Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:coolant-temperature"),
    ("Puff Füllgrad", "Buffer Fill Level", None, SensorStateClass.MEASUREMENT, "mdi:gauge"),
    ("Lagerstand", "Pellet Stock", None, SensorStateClass.TOTAL, "mdi:silo"),
    ("Verbrauchszähler", "Pellet Consumption", None, SensorStateClass.TOTAL_INCREASING, "mdi:basket-unfill"),
    ("TVL_1", "Flow 1 Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, "mdi:coolant-temperature"),
]

ADDITIONAL_SENSORS = [
    ("O2", "O2 Level", None, SensorStateClass.MEASUREMENT, None),
    ("O2soll", "O2 Target", None, SensorStateClass.MEASUREMENT, None),
    ("SZist", "Draft", None, SensorStateClass.MEASUREMENT, None),
    ("SZsoll", "Draft Target", None, SensorStateClass.MEASUREMENT, None),
    ("I Es", "Delivery Motor Current", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, None),
    ("I Sr", "Grate Motor Current", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, None),
    ("I Rein", "Cleaning Motor Current", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, None),
    ("TVL_2", "Flow 2 Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None),
    ("TVL_3", "Flow 3 Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None),
    ("TVL_4", "Flow 4 Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None),
    ("TVL_5", "Flow 5 Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None),
    ("TVL_6", "Flow 6 Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None),
    ("TB2", "Hot Water 2 Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None),
    ("TB3", "Hot Water 3 Temperature", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hargassner sensors from a config entry."""
    coordinator: HargassnerDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    device_name = entry.data.get(CONF_DEVICE_NAME, "Hargassner")
    sensor_set = entry.data.get(CONF_SENSOR_SET, "STANDARD")
    language = entry.data.get(CONF_LANGUAGE, "EN")

    entities: list[SensorEntity] = []

    # Always add connection sensor
    entities.append(HargassnerConnectionSensor(coordinator, entry))

    # Add boiler state sensor
    entities.append(HargassnerStateSensor(coordinator, entry, language))

    # Add error sensor
    entities.append(HargassnerErrorSensor(coordinator, entry, language))

    # Add energy sensor
    entities.append(HargassnerEnergySensor(coordinator, entry))

    # Add standard sensors
    for sensor_def in STANDARD_SENSORS:
        key, name, device_class, state_class, icon = sensor_def
        entities.append(
            HargassnerParameterSensor(
                coordinator,
                entry,
                key,
                f"{device_name} {name}",
                device_class,
                state_class,
                icon,
            )
        )

    # Add additional sensors if FULL mode
    if sensor_set == SENSOR_SET_FULL:
        for sensor_def in ADDITIONAL_SENSORS:
            key, name, device_class, state_class, icon = sensor_def
            entities.append(
                HargassnerParameterSensor(
                    coordinator,
                    entry,
                    key,
                    f"{device_name} {name}",
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
        )


class HargassnerConnectionSensor(HargassnerBaseSensor):
    """Sensor representing connection status."""

    _attr_icon = "mdi:network-outline"

    def __init__(
        self,
        coordinator: HargassnerDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize connection sensor."""
        super().__init__(coordinator, entry)
        self._attr_name = "Connection"
        self._attr_unique_id = f"{entry.entry_id}_connection"

    @property
    def native_value(self) -> str:
        """Return connection state."""
        if self.coordinator.telnet_client.connected:
            return STATE_CONNECTED
        return STATE_DISCONNECTED

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
        self._attr_name = "Boiler State"
        self._attr_unique_id = f"{entry.entry_id}_state"
        self._language = language
        self._attr_options = BOILER_STATES_DE if language == LANGUAGE_DE else BOILER_STATES_EN

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

        return "Unknown"

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
        self._attr_name = "Operation Status"
        self._attr_unique_id = f"{entry.entry_id}_operation"
        self._language = language
        self._attr_options = ["OK"] + [
            err[language.lower()] for err in ERROR_CODES.values()
        ]

    @property
    def native_value(self) -> str:
        """Return error status."""
        error_data = self.coordinator.data.get("Störung")

        if not error_data:
            return "OK"

        error_value = error_data.get("value")

        # Check if error is active
        if not error_value or error_value == "False" or error_value is False:
            return "OK"

        # Get error code
        error_code_data = self.coordinator.data.get("Störungs Nr")
        if error_code_data:
            error_code = str(error_code_data.get("value", ""))
            error_info = ERROR_CODES.get(error_code)

            if error_info:
                return error_info[self._language.lower()]

            return f"Error {error_code}"

        return "Error"

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
    ) -> None:
        """Initialize energy sensor."""
        super().__init__(coordinator, entry)
        self._attr_name = "Energy Consumption"
        self._attr_unique_id = f"{entry.entry_id}_energy"

    @property
    def native_value(self) -> float | None:
        """Return energy consumption in kWh."""
        pellet_data = self.coordinator.data.get("Verbrauchszähler")
        if pellet_data:
            try:
                pellets_kg = float(pellet_data.get("value", 0))
                return pellets_kg * PELLET_ENERGY_FACTOR
            except (ValueError, TypeError):
                pass
        return None
