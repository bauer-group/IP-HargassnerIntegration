"""Config flow for Hargassner Pellet Boiler integration."""
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
    CONF_DEVICE_NAME,
    CONF_EFFICIENCY,
    CONF_FIRMWARE,
    CONF_LANGUAGE,
    CONF_PELLET_ENERGY,
    CONF_SENSOR_SET,
    DEFAULT_EFFICIENCY,
    DEFAULT_PELLET_ENERGY,
    DOMAIN,
    FIRMWARE_VERSIONS,
    LANGUAGE_DE,
    LANGUAGE_EN,
    SENSOR_SET_FULL,
    SENSOR_SET_STANDARD,
)
from .exceptions import (
    HargassnerConnectionError,
    HargassnerTimeoutError,
)
from .src.telnet_client import HargassnerTelnetClient

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
            raise Exception("Failed to establish connection")

        return True

    finally:
        await client.async_stop()


class HargassnerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hargassner Pellet Boiler."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
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
                # Create entry
                return self.async_create_entry(
                    title=user_input.get(CONF_DEVICE_NAME, "Hargassner Boiler"),
                    data=user_input,
                )

        # Show form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_FIRMWARE, default="V14_1HAR_q1"): vol.In(
                    FIRMWARE_VERSIONS
                ),
                vol.Optional(CONF_DEVICE_NAME, default="Hargassner"): cv.string,
                vol.Optional(CONF_LANGUAGE, default=LANGUAGE_EN): vol.In(
                    [LANGUAGE_EN, LANGUAGE_DE]
                ),
                vol.Optional(CONF_SENSOR_SET, default=SENSOR_SET_STANDARD): vol.In(
                    [SENSOR_SET_STANDARD, SENSOR_SET_FULL]
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> HargassnerOptionsFlow:
        """Get the options flow for this handler."""
        return HargassnerOptionsFlow(config_entry)


class HargassnerOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Hargassner Pellet Boiler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

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

        # Get current values
        current_language = self.config_entry.data.get(CONF_LANGUAGE, LANGUAGE_EN)
        current_sensor_set = self.config_entry.data.get(
            CONF_SENSOR_SET, SENSOR_SET_STANDARD
        )
        current_pellet_energy = self.config_entry.data.get(
            CONF_PELLET_ENERGY, DEFAULT_PELLET_ENERGY
        )
        current_efficiency = self.config_entry.data.get(
            CONF_EFFICIENCY, DEFAULT_EFFICIENCY
        )

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_LANGUAGE, default=current_language): vol.In(
                    [LANGUAGE_EN, LANGUAGE_DE]
                ),
                vol.Optional(CONF_SENSOR_SET, default=current_sensor_set): vol.In(
                    [SENSOR_SET_STANDARD, SENSOR_SET_FULL]
                ),
                vol.Optional(
                    CONF_PELLET_ENERGY,
                    default=current_pellet_energy,
                    description={"suggested_value": current_pellet_energy}
                ): vol.All(vol.Coerce(float), vol.Range(min=3.0, max=6.0)),
                vol.Optional(
                    CONF_EFFICIENCY,
                    default=current_efficiency,
                    description={"suggested_value": current_efficiency}
                ): vol.All(vol.Coerce(int), vol.Range(min=50, max=100)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
        )
