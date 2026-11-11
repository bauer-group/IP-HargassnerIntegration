"""The Hargassner boiler integration (pellet and log wood)."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_BOILER_TYPE, CONF_FIRMWARE, DOMAIN, boiler_type_for_firmware
from .coordinator import HargassnerDataUpdateCoordinator
from .telnet_client import HargassnerTelnetClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a Hargassner boiler from a config entry."""
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
        coordinator: HargassnerDataUpdateCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.telnet_client.async_stop()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry.

    Goes through Home Assistant's reload so the entry passes through the proper
    states; calling async_setup_entry directly on a loaded entry is rejected by
    async_config_entry_first_refresh and left the integration unloaded.
    """
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate older config entries.

    Version 1 -> 2: add the boiler type. Entries on a log wood firmware template
    become log wood, everything else stays pellet. Sensor unique IDs do not
    change, so entity history is kept.
    """
    if entry.version > 2:
        # Downgrade from a future version - not supported
        return False

    if entry.version == 1:
        data = dict(entry.data)
        data.setdefault(CONF_BOILER_TYPE, boiler_type_for_firmware(data.get(CONF_FIRMWARE)))
        hass.config_entries.async_update_entry(entry, data=data, version=2)
        _LOGGER.info(
            "Migrated Hargassner config entry to version 2 (boiler type: %s)",
            data[CONF_BOILER_TYPE],
        )

    return True
