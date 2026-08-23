"""Type definitions for Hargassner Integration."""
from __future__ import annotations

from typing import TypedDict


class ParameterData(TypedDict):
    """Data structure for a single parameter."""

    value: float | int | str | bool
    unit: str | None
    timestamp: str | None


class StatisticsData(TypedDict):
    """Statistics data structure."""

    messages_received: int
    messages_parsed: int
    parse_errors: int
    reconnections: int
    last_error: str | None
    expected_length: int
    last_message_length: int


class BilingualText(TypedDict):
    """Bilingual text structure."""

    en: str
    de: str


class ConfigData(TypedDict, total=False):
    """Configuration data structure."""

    host: str
    firmware: str
    device_name: str
    language: str
    sensor_set: str
