"""Thread-safe telnet client for Hargassner boiler."""
from __future__ import annotations

import asyncio
import logging
import socket
from asyncio import StreamReader, StreamWriter
from collections.abc import Callable
from datetime import datetime

from .const import (
    TELNET_BUFFER_SIZE,
    TELNET_DATA_STALENESS_TIMEOUT,
    TELNET_PORT,
    TELNET_RECONNECT_DELAY,
    TELNET_TIMEOUT,
)
from .exceptions import HargassnerConnectionError, HargassnerTimeoutError
from .types import ParameterData, StatisticsData
from .message_parser import HargassnerMessageParser

_LOGGER = logging.getLogger(__name__)


class HargassnerTelnetClient:
    """Thread-safe telnet client with automatic reconnection."""

    def __init__(
        self,
        host: str,
        firmware_version: str,
        port: int = TELNET_PORT,
    ) -> None:
        """Initialize the telnet client.

        Args:
            host: IP address or hostname of the boiler
            firmware_version: Firmware version identifier (e.g., V14_1HAR_q1)
            port: Telnet port (default: 23)
        """
        self._host = host
        self._port = port
        self._firmware_version = firmware_version

        # Connection state
        self._reader: StreamReader | None = None
        self._writer: StreamWriter | None = None
        self._connected = False
        self._running = False

        # Background tasks
        self._receiver_task: asyncio.Task | None = None

        # Message parser
        self._parser = HargassnerMessageParser(firmware_version)

        # Data storage
        self._latest_data: dict[str, ParameterData] = {}
        self._data_lock = asyncio.Lock()
        self._last_update: datetime | None = None

        # Statistics
        self._stats: StatisticsData = {
            "messages_received": 0,
            "messages_parsed": 0,
            "parse_errors": 0,
            "reconnections": 0,
            "last_error": None,
        }

        # Callbacks
        self._data_callbacks: list[Callable[[dict[str, ParameterData]], None]] = []
        self._connection_callbacks: list[Callable[[bool], None]] = []

    async def async_start(self) -> None:
        """Start the telnet client and background receiver task."""
        if self._running:
            _LOGGER.warning("Telnet client already running")
            return

        _LOGGER.debug("Starting telnet client for %s:%d", self._host, self._port)
        self._running = True

        # Start receiver task
        self._receiver_task = asyncio.create_task(self._receiver_loop())

        # Wait for initial connection
        for _ in range(50):  # 5 seconds max
            if self._connected:
                _LOGGER.debug("Initial connection established")
                return
            await asyncio.sleep(0.1)

        _LOGGER.warning("Initial connection not established within timeout")

    async def async_stop(self) -> None:
        """Stop the telnet client and cleanup resources."""
        _LOGGER.debug("Stopping telnet client")
        self._running = False

        # Cancel receiver task
        if self._receiver_task and not self._receiver_task.done():
            self._receiver_task.cancel()
            try:
                await self._receiver_task
            except asyncio.CancelledError:
                pass

        # Close connection
        await self._close_connection()

    async def _receiver_loop(self) -> None:
        """Background loop that receives and processes telnet messages.

        Simple reconnect logic:
        1. TCP connection lost (OS-level) -> disconnect and reconnect
        2. No data received for 60s -> disconnect and reconnect
        """
        while self._running:
            try:
                # Ensure connection
                if not self._connected:
                    try:
                        await self._connect()
                    except (HargassnerConnectionError, HargassnerTimeoutError):
                        # Wait before retry
                        await asyncio.sleep(TELNET_RECONNECT_DELAY)
                        continue

                # Check for stale data (no data received for too long)
                # The boiler sends data every few seconds when powered on
                if self._last_update:
                    time_since_update = (datetime.now() - self._last_update).total_seconds()
                    if time_since_update > TELNET_DATA_STALENESS_TIMEOUT:
                        _LOGGER.warning(
                            "No data received for %.1f seconds, reconnecting",
                            time_since_update,
                        )
                        self._stats["last_error"] = f"Data stale for {time_since_update:.1f}s"
                        await self._close_connection()
                        continue

                # Read data
                if self._reader:
                    try:
                        data = await asyncio.wait_for(
                            self._reader.read(TELNET_BUFFER_SIZE),
                            timeout=TELNET_TIMEOUT,
                        )

                        if not data:
                            # TCP connection closed by server
                            _LOGGER.warning("Connection closed by server")
                            await self._close_connection()
                            continue

                        # Process received data
                        await self._process_data(data)

                    except asyncio.TimeoutError:
                        # Timeout is normal, just continue - staleness check handles dead connections
                        continue

            except OSError as err:
                # TCP connection lost (OS-level error)
                _LOGGER.warning("TCP connection lost: %s", err)
                self._stats["last_error"] = str(err)
                await self._close_connection()
                await asyncio.sleep(TELNET_RECONNECT_DELAY)

            except Exception as err:
                _LOGGER.error("Error in receiver loop: %s", err, exc_info=True)
                self._stats["last_error"] = str(err)
                await self._close_connection()
                await asyncio.sleep(TELNET_RECONNECT_DELAY)

    async def _connect(self) -> None:
        """Establish telnet connection to the boiler."""
        try:
            _LOGGER.debug("Connecting to %s:%d", self._host, self._port)

            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=TELNET_TIMEOUT,
            )

            # Enable TCP keepalive to detect dead connections
            sock = self._writer.get_extra_info("socket")
            if sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                # Platform-specific keepalive settings
                if hasattr(socket, "TCP_KEEPIDLE"):
                    # Linux: start keepalive after 30s idle
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
                if hasattr(socket, "TCP_KEEPINTVL"):
                    # Linux: send keepalive every 10s
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
                if hasattr(socket, "TCP_KEEPCNT"):
                    # Linux: close after 3 failed keepalives
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
                _LOGGER.debug("TCP keepalive enabled")

            self._set_connected(True)
            self._stats["reconnections"] += 1
            _LOGGER.debug("Connected to boiler")

        except asyncio.TimeoutError as err:
            _LOGGER.error("Connection timeout: %s", err)
            self._stats["last_error"] = f"Connection timeout: {err}"
            raise HargassnerTimeoutError(f"Connection to {self._host}:{self._port} timed out") from err
        except OSError as err:
            _LOGGER.error("Failed to connect: %s", err)
            self._stats["last_error"] = f"Connection failed: {err}"
            raise HargassnerConnectionError(f"Failed to connect to {self._host}:{self._port}: {err}") from err

    async def _close_connection(self) -> None:
        """Close the telnet connection."""
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception as err:
                _LOGGER.debug("Error closing connection: %s", err)
            finally:
                self._writer = None
                self._reader = None

        self._set_connected(False)

    async def _process_data(self, data: bytes) -> None:
        """Process received telnet data.

        Args:
            data: Raw bytes received from telnet
        """
        self._stats["messages_received"] += 1

        try:
            # Try multiple encodings
            text = None
            for encoding in ["utf-8", "latin-1", "cp1252"]:
                try:
                    text = data.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if text is None:
                # Fallback: replace invalid characters
                text = data.decode("utf-8", errors="replace")
                _LOGGER.debug("Used fallback decoding with character replacement")

            # Split into lines and process each
            lines = text.strip().split("\n")

            for line in lines:
                line = line.strip()
                if not line or not line.startswith("pm"):
                    continue

                # Parse message
                try:
                    parsed_data = self._parser.parse_message(line)

                    if parsed_data:
                        # Store data
                        async with self._data_lock:
                            self._latest_data = parsed_data
                            self._last_update = datetime.now()

                        self._stats["messages_parsed"] += 1

                        # Notify callbacks
                        for callback in self._data_callbacks:
                            try:
                                callback(parsed_data)
                            except Exception as err:
                                _LOGGER.error("Error in data callback: %s", err)

                        # Only process the most recent message
                        break

                except Exception as err:
                    _LOGGER.warning("Failed to parse message: %s", err)
                    self._stats["parse_errors"] += 1

        except Exception as err:
            _LOGGER.error("Error processing data: %s", err, exc_info=True)
            self._stats["parse_errors"] += 1

    async def get_latest_data(self) -> dict[str, ParameterData]:
        """Get the latest parsed data.

        Returns:
            Dictionary with latest boiler parameters
        """
        async with self._data_lock:
            return self._latest_data.copy()

    def register_callback(self, callback: Callable[[dict[str, ParameterData]], None]) -> None:
        """Register a callback for new data.

        Args:
            callback: Function to call when new data is available
        """
        if callback not in self._data_callbacks:
            self._data_callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[dict[str, ParameterData]], None]) -> None:
        """Unregister a data callback.

        Args:
            callback: Function to remove from callbacks
        """
        if callback in self._data_callbacks:
            self._data_callbacks.remove(callback)

    def register_connection_callback(self, callback: Callable[[bool], None]) -> None:
        """Register a callback for connection state changes.

        Args:
            callback: Function to call when connection state changes (receives bool: connected)
        """
        if callback not in self._connection_callbacks:
            self._connection_callbacks.append(callback)

    def unregister_connection_callback(self, callback: Callable[[bool], None]) -> None:
        """Unregister a connection state callback.

        Args:
            callback: Function to remove from callbacks
        """
        if callback in self._connection_callbacks:
            self._connection_callbacks.remove(callback)

    def _set_connected(self, connected: bool) -> None:
        """Set connection state and notify callbacks.

        Args:
            connected: New connection state
        """
        if self._connected != connected:
            self._connected = connected
            _LOGGER.debug("Connection state changed to: %s", connected)
            for callback in self._connection_callbacks:
                try:
                    callback(connected)
                except Exception as err:
                    _LOGGER.error("Error in connection callback: %s", err)

    @property
    def connected(self) -> bool:
        """Return connection status."""
        return self._connected

    @property
    def last_update(self) -> datetime | None:
        """Return timestamp of last successful update."""
        return self._last_update

    @property
    def statistics(self) -> StatisticsData:
        """Return client statistics."""
        return self._stats.copy()

    @property
    def expected_message_length(self) -> int:
        """Return expected message length for current firmware."""
        return self._parser.expected_length
