"""Shared test fixtures.

The integration package cannot be imported directly: its ``__init__.py`` imports
Home Assistant, which is not a test dependency. The standalone-tool shim in
``tools/_integration_import.py`` loads the pure-Python modules by file path
instead, which is the same route the developer tools use.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from _integration_import import load_module  # noqa: E402

firmware_templates = load_module("firmware_templates")
message_parser = load_module("message_parser")

FIRMWARE_TEMPLATES = firmware_templates.FIRMWARE_TEMPLATES
HargassnerMessageParser = message_parser.HargassnerMessageParser

import message_generator  # noqa: E402

MessageGenerator = message_generator.MessageGenerator
BOILER_STATES = message_generator.BOILER_STATES


@dataclass
class Geometry:
    """Message layout read straight from the DAQPRJ template.

    Derived from the XML rather than from the parser or the generator on purpose:
    if the expectations came from either, a matching pair of bugs would cancel out
    and the round-trip test would pass while both sides were wrong.
    """

    analog_count: int
    digital_word_count: int
    analog: dict[int, tuple[str, str | None]] = field(default_factory=dict)
    declared_mask: dict[int, int] = field(default_factory=dict)
    digital_channels: list[tuple[str, int, int]] = field(default_factory=list)

    @property
    def expected_length(self) -> int:
        """Total number of values in a message."""
        return self.analog_count + self.digital_word_count


def build_geometry(firmware: str) -> Geometry:
    """Parse a firmware template into its message layout."""
    root = ET.fromstring(FIRMWARE_TEMPLATES[firmware])

    analog: dict[int, tuple[str, str | None]] = {}
    for channel in root.findall(".//ANALOG/CHANNEL"):
        analog[int(channel.get("id"))] = (channel.get("name", ""), channel.get("dop"))

    declared_mask: dict[int, int] = {}
    digital_channels: list[tuple[str, int, int]] = []
    for channel in root.findall(".//DIGITAL/CHANNEL"):
        word = int(channel.get("id"))
        bit = int(channel.get("bit", 0))
        declared_mask[word] = declared_mask.get(word, 0) | (1 << bit)
        digital_channels.append((channel.get("name", ""), word, bit))

    return Geometry(
        analog_count=max(analog) + 1 if analog else 0,
        digital_word_count=max(declared_mask) + 1 if declared_mask else 0,
        analog=analog,
        declared_mask=declared_mask,
        digital_channels=digital_channels,
    )


@pytest.fixture(params=sorted(FIRMWARE_TEMPLATES), ids=str)
def firmware_key(request: pytest.FixtureRequest) -> str:
    """Each bundled firmware template in turn."""
    return request.param


@pytest.fixture
def geometry(firmware_key: str) -> Geometry:
    """Message layout for the firmware under test."""
    return build_geometry(firmware_key)


@pytest.fixture
def parser(firmware_key: str):
    """Parser for the firmware under test."""
    return HargassnerMessageParser(firmware_key)


@pytest.fixture
def generator(firmware_key: str):
    """Seeded generator for the firmware under test."""
    return MessageGenerator(firmware_key, seed=20260823)
