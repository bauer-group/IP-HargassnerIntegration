"""Sensor platform for Hargassner boilers (pellet and log wood)."""
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

from .boiler_profiles import (
    ENERGY_BUFFER_STORED,
    BoilerProfile,
    buffer_stored_energy_kwh,
    get_profile,
)
from .const import (
    CONF_BOILER_TYPE,
    CONF_BUFFER_REFERENCE,
    CONF_BUFFER_VOLUME,
    CONF_DEVICE_NAME,
    CONF_EFFICIENCY,
    CONF_FIRMWARE,
    CONF_LANGUAGE,
    CONF_PELLET_ENERGY,
    CONF_SENSOR_SET,
    DEFAULT_BUFFER_REFERENCE,
    DEFAULT_BUFFER_VOLUME,
    DEFAULT_EFFICIENCY,
    DEFAULT_PELLET_ENERGY,
    DOMAIN,
    LANGUAGE_DE,
    boiler_type_for_firmware,
    SENSOR_SET_FULL,
    STATE_CONNECTED,
    STATE_DISCONNECTED,
)
from .coordinator import HargassnerDataUpdateCoordinator
from .firmware_templates import PARAMETER_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)

# Bidirectional mapping for parameter name variants (umlauts vs ASCII-normalized)
# Some firmware templates use German umlauts, others use ASCII replacements
_PARAM_NAME_ALIASES: dict[str, str] = {
    "Verbrauchszähler": "Verbrauchszaehler",
    "Verbrauchszaehler": "Verbrauchszähler",
    "Störungs Nr": "Storungs Nr",
    "Storungs Nr": "Störungs Nr",
    "Stoerungs Nr": "Störungs Nr",
    "Puff Füllgrad": "Puff Fuellgrad",
    "Puff Fuellgrad": "Puff Füllgrad",
}


def _get_param_data(data: dict, key: str) -> dict | None:
    """Get parameter data with umlaut-normalized fallback."""
    result = data.get(key)
    if result is not None:
        return result
    alt_key = _PARAM_NAME_ALIASES.get(key)
    if alt_key:
        return data.get(alt_key)
    return None


# =============================================================================
# SENSOR SETS
# =============================================================================
# Automatisch erstellte Sensoren (immer aktiv, bei STANDARD und FULL):
#   - Verbindung        : Telnet-Verbindungsstatus (connected/disconnected)
#   - Kesselzustand     : Aktueller Kesselzustand (ZK-Wert als Text)
#   - Betriebsstatus    : Aktive Störungsnummer und Beschreibung
#   - Energie           : Pellet: Wärmemenge aus Pelletverbrauch
#                         Stückholz: im Puffer gespeicherte Energie
#
# Welche Parameter-Sensoren das STANDARD-Set enthält, legt das Kesselprofil
# fest (boiler_profiles.py). FULL erzeugt Sensoren für alle Template-Parameter.
# =============================================================================


def profile_for_entry(entry: ConfigEntry) -> BoilerProfile:
    """Return the boiler profile of a config entry.

    Falls back to the firmware's boiler type for entries not yet migrated.
    """
    boiler_type = entry.data.get(CONF_BOILER_TYPE) or boiler_type_for_firmware(
        entry.data.get(CONF_FIRMWARE)
    )
    return get_profile(boiler_type)


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

    # Add energy sensor - how energy is derived depends on the boiler type
    profile = profile_for_entry(entry)
    if profile.energy_kind == ENERGY_BUFFER_STORED:
        entities.append(HargassnerBufferEnergySensor(coordinator, entry, language))
    else:
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
                if param_name in ["Verbrauchszähler", "Verbrauchszaehler", "Brennerstarts", "Betriebsstunden"]:
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
        # STANDARD mode: the boiler profile's predefined sensors
        for key, name, device_class_str, state_class_str, icon in profile.standard_sensors:
            device_class = SensorDeviceClass(device_class_str) if device_class_str else None
            state_class = SensorStateClass(state_class_str) if state_class_str else None
            desc = PARAMETER_DESCRIPTIONS.get(key, {})
            display_name = desc.get(language.lower(), name)
            entities.append(
                HargassnerParameterSensor(
                    coordinator,
                    entry,
                    key,
                    display_name,  # No device prefix - handled by has_entity_name
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
            model=profile_for_entry(entry).model,
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
            # Template fit: if these two differ, the selected firmware template does
            # not match this boiler and values may land in the wrong entities
            "firmware_template": self._entry.data.get("firmware"),
            "expected_length": stats.get("expected_length", 0),
            "last_message_length": stats.get("last_message_length", 0),
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
        self._profile = profile_for_entry(entry)
        self._attr_options = self._profile.state_options(language)
        fallback = self._profile.state_name(-1, language)
        if not self._profile.unknown_state_as_number and fallback not in self._attr_options:
            self._attr_options.append(fallback)

    def _zk(self) -> int | None:
        """Current ZK value, or None if not available."""
        zk_data = _get_param_data(self.coordinator.data, "ZK")
        if not zk_data:
            return None
        try:
            return int(zk_data.get("value", 0))
        except (ValueError, TypeError):
            return None

    @property
    def native_value(self) -> str | None:
        """Return boiler state."""
        zk = self._zk()
        if zk is None:
            # ZK missing, or present but not a number
            if self._profile.unknown_state_as_number or not _get_param_data(
                self.coordinator.data, "ZK"
            ):
                return None
            return self._profile.state_name(-1, self._language)

        name = self._profile.state_name(zk, self._language)
        # Unnamed states ("ZK 5") are added on the fly so the ENUM stays valid
        if name not in self._attr_options:
            self._attr_options.append(name)
        return name

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the raw ZK value, which helps naming new states."""
        return {"zk": self._zk()}

    @property
    def icon(self) -> str:
        """Return icon based on state."""
        zk = self._zk()
        if zk is not None and zk in self._profile.firing_states:
            return "mdi:fireplace"
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
        self._profile = profile_for_entry(entry)
        self._attr_options = ["OK"] + [
            err[language.lower()] for err in self._profile.error_codes.values()
        ]

    @property
    def native_value(self) -> str:
        """Return error status."""
        # Get error code from "Störungs Nr" analog parameter
        # 0 = no error, >0 = error code
        error_code_data = _get_param_data(self.coordinator.data, "Störungs Nr")

        if not error_code_data:
            return "OK"

        error_code = str(int(error_code_data.get("value", 0)))

        if error_code == "0":
            return "OK"

        # Error is present - look up description
        error_text = self._profile.error_name(error_code, self._language)
        if error_text:
            return error_text

        # Unknown error code - add to options dynamically for ENUM compatibility
        lang = self._language.lower()
        fallback = f"Error {error_code}" if lang == "en" else f"Fehler {error_code}"
        if fallback not in self._attr_options:
            self._attr_options.append(fallback)
        return fallback

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
        param_data = _get_param_data(self.coordinator.data, self._param_key)
        if param_data:
            return param_data.get("value")
        return None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement."""
        param_data = _get_param_data(self.coordinator.data, self._param_key)
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
        pellet_data = _get_param_data(self.coordinator.data, "Verbrauchszähler")
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


class HargassnerBufferEnergySensor(HargassnerBaseSensor):
    """Heat stored in the buffer tank (log wood boilers).

    kWh above the configured reference temperature, from the mean of the three
    buffer sensors and the buffer volume. Rises while the boiler charges the
    buffer and falls while the house draws from it.
    """

    _attr_device_class = SensorDeviceClass.ENERGY_STORAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 1
    _attr_icon = "mdi:heat-wave"

    _SENSORS = ("TPo", "TPm", "TPu")

    def __init__(
        self,
        coordinator: HargassnerDataUpdateCoordinator,
        entry: ConfigEntry,
        language: str,
    ) -> None:
        """Initialize buffer energy sensor."""
        super().__init__(coordinator, entry)
        self._attr_name = (
            "Buffer Stored Energy" if language.upper() == "EN" else "Puffer Energieinhalt"
        )
        # New unique ID on purpose: this is a stored-energy measurement, not the
        # pellet sensor's ever-increasing total, so it must not inherit its
        # long-term statistics.
        self._attr_unique_id = f"{entry.entry_id}_buffer_energy"
        self._entry = entry

    def _temperatures(self) -> list[float] | None:
        temps: list[float] = []
        for key in self._SENSORS:
            data = _get_param_data(self.coordinator.data, key)
            if not data:
                return None
            try:
                temps.append(float(data.get("value")))
            except (ValueError, TypeError):
                return None
        return temps

    @property
    def native_value(self) -> float | None:
        """Return stored energy in kWh."""
        temps = self._temperatures()
        if temps is None:
            return None
        volume = self._entry.data.get(CONF_BUFFER_VOLUME, DEFAULT_BUFFER_VOLUME)
        reference = self._entry.data.get(CONF_BUFFER_REFERENCE, DEFAULT_BUFFER_REFERENCE)
        return round(buffer_stored_energy_kwh(temps, volume, reference), 2)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the inputs of the calculation."""
        temps = self._temperatures()
        volume = self._entry.data.get(CONF_BUFFER_VOLUME, DEFAULT_BUFFER_VOLUME)
        reference = self._entry.data.get(CONF_BUFFER_REFERENCE, DEFAULT_BUFFER_REFERENCE)
        return {
            "buffer_volume_l": volume,
            "reference_temperature_c": reference,
            "mean_buffer_temperature_c": round(sum(temps) / len(temps), 1) if temps else None,
            "kwh_per_kelvin": round(volume * 1.163 / 1000.0, 3),
            "calculation": f"{volume} l × 1.163 Wh/(l·K) × (mean buffer temperature − {reference} °C)",
        }
