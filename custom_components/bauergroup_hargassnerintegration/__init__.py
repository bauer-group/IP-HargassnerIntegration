"""The Hargassner Pellet Boiler integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import HargassnerDataUpdateCoordinator
from .telnet_client import HargassnerTelnetClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hargassner Pellet Boiler from a config entry."""
    _LOGGER.debug("Setting up Hargassner integration for %s", entry.data.get(CONF_HOST))

    # Create telnet client
    telnet_client = HargassnerTelnetClient(
        host=entry.data[CONF_HOST],
        firmware_version=entry.data.get("firmware", "V14_1HAR_q1"),
    )

    # Create coordinator
    coordinator = HargassnerDataUpdateCoordinator(
        hass=hass,
        telnet_client=telnet_client,
        entry=entry,
    )

    # Start telnet client and wait for initial data
    try:
        await telnet_client.async_start()
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        await telnet_client.async_stop()
        raise ConfigEntryNotReady(f"Failed to connect to boiler: {err}") from err

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register options update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Hargassner integration")

    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: HargassnerDataUpdateCoordinator | None = hass.data.get(DOMAIN, {}).pop(
            entry.entry_id, None
        )
        if coordinator is not None:
            await coordinator.telnet_client.async_stop()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry through Home Assistant.

    Calling async_unload_entry/async_setup_entry directly bypasses the entry's
    state machine: async_config_entry_first_refresh then runs on a LOADED entry
    and fails, and the options flow fires this listener twice (data + options),
    so the second unload hit a KeyError and left the entry in failed_unload.
    """
    await hass.config_entries.async_reload(entry.entry_id)
