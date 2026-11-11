"""Config flow for the Hargassner boiler integration (pellet and log wood)."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    BOILER_TYPE_LOG_WOOD,
    BOILER_TYPE_PELLET,
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
    boiler_type_for_firmware,
    firmware_versions_for,
    LANGUAGE_DE,
    LANGUAGE_EN,
    SENSOR_SET_FULL,
    SENSOR_SET_STANDARD,
)
from .exceptions import (
    HargassnerConnectionError,
    HargassnerTimeoutError,
)
from .telnet_client import HargassnerTelnetClient

_LOGGER = logging.getLogger(__name__)


async def validate_connection(hass: HomeAssistant, host: str, firmware: str) -> bool:
    """Validate that we can connect to the boiler.

    Args:
        hass: Home Assistant instance
        host: Boiler IP address or hostname
        firmware: Firmware version

    Returns:
        True if connection successful

    Raises:
        Exception if connection fails
    """
    client = HargassnerTelnetClient(host=host, firmware_version=firmware)

    try:
        await client.async_start()
        await asyncio.sleep(2)  # Wait for initial data

        if not client.connected:
            raise HargassnerConnectionError("Failed to establish connection")

        return True

    finally:
        await client.async_stop()


DEFAULT_FIRMWARE: dict[str, str] = {
    BOILER_TYPE_PELLET: "V14_1HAR_q1",
    BOILER_TYPE_LOG_WOOD: "V10_2HAR_n2",
}


def _type_settings_schema(boiler_type: str, current: dict[str, Any]) -> dict:
    """Fields that only apply to one boiler type, with current values as defaults."""
    if boiler_type == BOILER_TYPE_LOG_WOOD:
        return {
            vol.Optional(
                CONF_BUFFER_VOLUME,
                default=current.get(CONF_BUFFER_VOLUME, DEFAULT_BUFFER_VOLUME),
            ): vol.All(vol.Coerce(int), vol.Range(min=100, max=20000)),
            vol.Optional(
                CONF_BUFFER_REFERENCE,
                default=current.get(CONF_BUFFER_REFERENCE, DEFAULT_BUFFER_REFERENCE),
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=60)),
        }
    return {
        vol.Optional(
            CONF_PELLET_ENERGY,
            default=current.get(CONF_PELLET_ENERGY, DEFAULT_PELLET_ENERGY),
        ): vol.All(vol.Coerce(float), vol.Range(min=3.0, max=6.0)),
        vol.Optional(
            CONF_EFFICIENCY,
            default=current.get(CONF_EFFICIENCY, DEFAULT_EFFICIENCY),
        ): vol.All(vol.Coerce(int), vol.Range(min=50, max=100)),
    }


def _common_schema(boiler_type: str, current: dict[str, Any]) -> dict:
    """Firmware, language and sensor set - the firmware list depends on the type."""
    firmwares = firmware_versions_for(boiler_type)
    default_fw = current.get(CONF_FIRMWARE, DEFAULT_FIRMWARE[boiler_type])
    if default_fw not in firmwares:
        default_fw = firmwares[0]
    return {
        vol.Required(CONF_FIRMWARE, default=default_fw): vol.In(firmwares),
        vol.Optional(
            CONF_LANGUAGE, default=current.get(CONF_LANGUAGE, LANGUAGE_EN)
        ): vol.In([LANGUAGE_EN, LANGUAGE_DE]),
        vol.Optional(
            CONF_SENSOR_SET, default=current.get(CONF_SENSOR_SET, SENSOR_SET_STANDARD)
        ): vol.In([SENSOR_SET_STANDARD, SENSOR_SET_FULL]),
    }


class HargassnerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hargassner boilers.

    Step 1 (user): boiler type. Step 2 (connection): host, firmware and the
    settings that apply to that type.
    """

    VERSION = 2

    def __init__(self) -> None:
        """Initialize the flow."""
        self._boiler_type: str = BOILER_TYPE_PELLET

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Ask which kind of boiler this is."""
        if user_input is not None:
            self._boiler_type = user_input[CONF_BOILER_TYPE]
            return await self.async_step_connection()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BOILER_TYPE, default=BOILER_TYPE_PELLET): vol.In(
                        {
                            BOILER_TYPE_PELLET: "Pellet (Nano-PK, Classic, HSV, ...)",
                            BOILER_TYPE_LOG_WOOD: "Log wood (HV, Neo-HV)",
                        }
                    ),
                }
            ),
        )

    async def async_step_connection(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Connection details and type-specific settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate unique entry per host
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            # Test connection
            try:
                await validate_connection(
                    self.hass,
                    user_input[CONF_HOST],
                    user_input[CONF_FIRMWARE],
                )
            except HargassnerTimeoutError:
                _LOGGER.error("Connection timeout")
                errors["base"] = "timeout"
            except HargassnerConnectionError:
                _LOGGER.error("Connection failed")
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.exception("Unexpected error during connection test: %s", err)
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input.get(CONF_DEVICE_NAME, "Hargassner Boiler"),
                    data={**user_input, CONF_BOILER_TYPE: self._boiler_type},
                )

        current = user_input or {}
        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current.get(CONF_HOST, vol.UNDEFINED)): cv.string,
                vol.Optional(
                    CONF_DEVICE_NAME, default=current.get(CONF_DEVICE_NAME, "Hargassner")
                ): cv.string,
                **_common_schema(self._boiler_type, current),
                **_type_settings_schema(self._boiler_type, current),
            }
        )

        return self.async_show_form(
            step_id="connection",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"boiler_type": self._boiler_type},
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> HargassnerOptionsFlow:
        """Get the options flow for this handler."""
        return HargassnerOptionsFlow()


class HargassnerOptionsFlow(config_entries.OptionsFlow):
    """Handle options. The boiler type is fixed; its own settings are shown."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            # Update entry.data with new options (options alone won't reload sensors)
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input}
            )
            return self.async_create_entry(title="", data=user_input)

        current = dict(self.config_entry.data)
        boiler_type = current.get(CONF_BOILER_TYPE) or boiler_type_for_firmware(
            current.get(CONF_FIRMWARE)
        )

        data_schema = vol.Schema(
            {
                **_common_schema(boiler_type, current),
                **_type_settings_schema(boiler_type, current),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            description_placeholders={"boiler_type": boiler_type},
        )
