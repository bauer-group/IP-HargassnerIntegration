"""Message parser for Hargassner telnet protocol."""
from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from typing import Any

from .firmware_templates import FIRMWARE_TEMPLATES, PARAMETER_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)


class ParameterDefinition:
    """Definition of a single parameter from firmware template."""

    def __init__(
        self,
        name: str,
        index: int,
        unit: str | None = None,
        is_digital: bool = False,
        bit_mask: int | None = None,
    ) -> None:
        """Initialize parameter definition.

        Args:
            name: Parameter name (e.g., 'TK', 'O2')
            index: Position in message array
            unit: Unit of measurement (e.g., '°C', '%')
            is_digital: Whether this is a digital (boolean) parameter
            bit_mask: For digital parameters, the bit mask to extract value
        """
        self.name = name
        self.index = index
        self.unit = unit
        self.is_digital = is_digital
        self.bit_mask = bit_mask
        self.description = PARAMETER_DESCRIPTIONS.get(name, name)

    def parse_value(self, values: list[str]) -> Any:
        """Parse value from message array.

        Args:
            values: List of string values from telnet message

        Returns:
            Parsed value (float, int, or bool)
        """
        if self.index >= len(values):
            return None

        try:
            raw_value = values[self.index]

            if self.is_digital and self.bit_mask is not None:
                # Digital parameter - extract bit.
                # Digital words arrive as UPPERCASE HEXADECIMAL, so a word may be a
                # token like 'E' or '2007'. Read base 10 they either raise (dropping
                # every channel of that word) or set bits no channel declares.
                int_value = int(raw_value, 16)
                return bool(int_value & self.bit_mask)

            # Analog parameter - convert to number
            # Try float first, fallback to int
            if "." in raw_value:
                return float(raw_value)
            return int(raw_value)

        except (ValueError, IndexError) as err:
            _LOGGER.debug(
                "Failed to parse value for %s at index %d: %s",
                self.name,
                self.index,
                err,
            )
            return None


class HargassnerMessageParser:
    """Parser for Hargassner telnet messages."""

    def __init__(self, firmware_version: str) -> None:
        """Initialize message parser.

        Args:
            firmware_version: Firmware version identifier
        """
        self._firmware_version = firmware_version
        self._parameters: dict[str, ParameterDefinition] = {}
        self._expected_length = 0
        self._last_message_length = 0
        # Length of the last message we already warned about - the boiler pushes a
        # message every few seconds, so warn only when the mismatch actually changes
        self._warned_length: int | None = None

        # Parse firmware template
        self._parse_template()

    def _parse_template(self) -> None:
        """Parse XML firmware template and build parameter definitions."""
        template = FIRMWARE_TEMPLATES.get(self._firmware_version)

        if not template:
            _LOGGER.error(
                "Unknown firmware version: %s, using V14_1HAR_q1 as fallback",
                self._firmware_version,
            )
            template = FIRMWARE_TEMPLATES["V14_1HAR_q1"]

        try:
            root = ET.fromstring(template)

            # Parse analog parameters
            analog_count = 0
            for channel in root.findall(".//ANALOG/CHANNEL"):
                param_id = int(channel.get("id", 0))
                param_name = channel.get("name", f"Unknown_{param_id}")
                param_unit = channel.get("unit")

                self._parameters[param_name] = ParameterDefinition(
                    name=param_name,
                    index=param_id,
                    unit=param_unit if param_unit else None,
                    is_digital=False,
                )

                analog_count = max(analog_count, param_id + 1)

            # Parse digital parameters
            digital_offset = analog_count
            digital_count = 0

            for channel in root.findall(".//DIGITAL/CHANNEL"):
                param_id = int(channel.get("id", 0))
                param_name = channel.get("name", f"Digital_{param_id}")
                param_bit = int(channel.get("bit", 0))

                self._parameters[param_name] = ParameterDefinition(
                    name=param_name,
                    index=digital_offset + param_id,
                    is_digital=True,
                    bit_mask=1 << param_bit,
                )

                digital_count = max(digital_count, param_id + 1)

            self._expected_length = analog_count + digital_count

            _LOGGER.info(
                "Parsed template for %s: %d analog + %d digital = %d total parameters",
                self._firmware_version,
                analog_count,
                digital_count,
                len(self._parameters),
            )

        except ET.ParseError as err:
            _LOGGER.error("Failed to parse firmware template: %s", err)
            raise

    def parse_message(self, message: str) -> dict[str, Any] | None:
        """Parse a telnet message line.

        Args:
            message: Raw message line from telnet (starting with 'pm')

        Returns:
            Dictionary with parsed parameters, or None if parsing failed
        """
        # Remove 'pm' prefix and split into values
        parts = message.strip().split()

        if not parts or parts[0] != "pm":
            _LOGGER.debug("Message does not start with 'pm': %s", message[:50])
            return None

        values = parts[1:]  # Skip 'pm' prefix

        # Check message length
        self._last_message_length = len(values)

        if len(values) != self._expected_length:
            # Don't fail completely - a boiler with extra boards sends more values
            # than the template declares, and the leading parameters still line up.
            # But surface it: every index after the first divergence may be wrong,
            # which shows up as plausible-looking values in the wrong entities.
            if self._warned_length != len(values):
                self._warned_length = len(values)
                _LOGGER.warning(
                    "Message length mismatch for firmware template '%s': expected %d "
                    "values, boiler sent %d. Parameter values may be assigned to the "
                    "wrong entities. Pick a matching template in the integration "
                    "options, or report the raw message so a template can be added",
                    self._firmware_version,
                    self._expected_length,
                    len(values),
                )
        elif self._warned_length is not None:
            self._warned_length = None
            _LOGGER.info(
                "Message length now matches firmware template '%s' (%d values)",
                self._firmware_version,
                self._expected_length,
            )

        # Parse all parameters
        parsed_data: dict[str, Any] = {}

        for param_name, param_def in self._parameters.items():
            value = param_def.parse_value(values)

            if value is not None:
                parsed_data[param_name] = {
                    "value": value,
                    "unit": param_def.unit,
                    "description": param_def.description,
                }

        return parsed_data

    @property
    def expected_length(self) -> int:
        """Return expected message length."""
        return self._expected_length

    @property
    def last_message_length(self) -> int:
        """Return the value count of the most recently parsed message."""
        return self._last_message_length

    @property
    def parameters(self) -> list[ParameterDefinition]:
        """Return all parameter definitions as list."""
        return list(self._parameters.values())

    def get_parameter_info(self, name: str) -> ParameterDefinition | None:
        """Get parameter definition by name.

        Args:
            name: Parameter name

        Returns:
            Parameter definition or None if not found
        """
        return self._parameters.get(name)
