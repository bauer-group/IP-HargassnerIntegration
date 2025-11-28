"""Data update coordinator for Hargassner Pellet Boiler."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .telnet_client import HargassnerTelnetClient

_LOGGER = logging.getLogger(__name__)


class HargassnerDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Hargassner data from telnet client.

    Uses push-based updates: sensors are updated immediately when new data
    arrives from the boiler, rather than polling at fixed intervals.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        telnet_client: HargassnerTelnetClient,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance
            telnet_client: Telnet client instance
            entry: Config entry
        """
        self.telnet_client = telnet_client
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            # Pure push-based: Callbacks update sensors immediately when data arrives
            # No automatic polling - _async_update_data() available for manual refresh
            update_interval=None,
        )

        # Register callbacks for push-based updates
        self.telnet_client.register_callback(self._handle_data_update)
        self.telnet_client.register_connection_callback(self._handle_connection_change)

    @callback
    def _handle_data_update(self, data: dict[str, Any]) -> None:
        """Handle new data from telnet client (push-based).

        Args:
            data: New boiler data from telnet client
        """
        # Add connection metadata
        data["_connection"] = {
            "connected": self.telnet_client.connected,
            "last_update": self.telnet_client.last_update,
            "statistics": self.telnet_client.statistics,
        }

        # Push update to all listeners (sensors)
        self.async_set_updated_data(data)

    @callback
    def _handle_connection_change(self, connected: bool) -> None:
        """Handle connection state change from telnet client.

        Args:
            connected: New connection state
        """
        _LOGGER.debug("Connection state changed: %s", connected)

        # Update existing data with new connection state, or create minimal data
        current_data = self.data or {}
        current_data["_connection"] = {
            "connected": connected,
            "last_update": self.telnet_client.last_update,
            "statistics": self.telnet_client.statistics,
        }

        # Push update to refresh connection sensor
        self.async_set_updated_data(current_data)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fallback method for manual refresh requests.

        This is called when async_refresh() is invoked (e.g., after HA restart).
        Primary updates come via push callbacks, but this provides a fallback.

        Returns:
            Dictionary with latest boiler data
        """
        # Return cached data with updated connection info
        data = await self.telnet_client.get_latest_data()

        if data:
            data["_connection"] = {
                "connected": self.telnet_client.connected,
                "last_update": self.telnet_client.last_update,
                "statistics": self.telnet_client.statistics,
            }

        return data or {}
