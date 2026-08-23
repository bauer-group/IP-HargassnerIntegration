"""Tests for the telnet message parser."""

from __future__ import annotations

import logging

import pytest

from conftest import (
    FIRMWARE_TEMPLATES,
    HargassnerMessageParser,
    build_geometry,
)

# A verbatim telnet line from a Nano.2(.3) 15, contributed in Issue #17, captured
# while the boiler was switched off. 155 values, an exact match for its template.
REAL_CAPTURE = (
    "pm 1 1.1 8.1 67.7 0 70.1 32 14 69.9 0 0 68.5 69.1 67.8 100 5 0 0 0 68 0 0 30 "
    "100 30 30 54 93.5 98 3 0 0 7 2 0 0 0 99 38 0 1838 3006 4814 0.00 0.00 -3 50.9 "
    "24208 140.0 119.3 37 -20.0 -20.0 0.0 5.2 8.8 0.0 1 3 0 0 -20.0 0 20.0 20.0 0 1 "
    "0 34.7 0 20.9 21.1 4 1 32 120.0 0 20.0 20.0 0 1 0 31.3 0 26.2 21.0 4 1 32 120.0 "
    "0 20.0 20.0 0 1 0 -20.0 0 20.0 20.0 0 1 0 -20.0 0 60.3 0 0 0 71.8 0 0 0 -20.0 0 "
    "0.0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 2.5 2.5 0.0 70.8 120.0 62.2 100 0 5 0 0 0 "
    "0 0.00 406 0 0 0 1 0 0 0"
)
REAL_CAPTURE_FIRMWARE = "V14_1HAR_q_nano2_zuspuf_aup3"

EXPECTED_LENGTHS = {
    "V14_0HAR_q": 120,
    "V14_0d": 171,
    "V14_0m5": 154,
    "V14_1HAR_q1": 121,
    "V14_1HAR_q1_solar": 140,
    "V14_1HAR_q_nano2_zuspuf_aup3": 155,
    "V40_0HAR_az15": 157,
}


def test_expected_lengths_are_pinned(firmware_key, parser):
    """Protocol lengths do not move without a deliberate edit."""
    assert set(FIRMWARE_TEMPLATES) == set(EXPECTED_LENGTHS)
    assert parser.expected_length == EXPECTED_LENGTHS[firmware_key]


def test_real_capture_parses_completely():
    """A real telnet line yields every parameter the template declares."""
    parser = HargassnerMessageParser(REAL_CAPTURE_FIRMWARE)
    geometry = build_geometry(REAL_CAPTURE_FIRMWARE)

    assert len(REAL_CAPTURE.split()) - 1 == parser.expected_length == 155

    parsed = parser.parse_message(REAL_CAPTURE)

    assert parsed is not None
    assert [p.name for p in parser.parameters if p.name not in parsed] == []

    # Analog spot checks against the boiler's own readings
    assert parsed["ZK"]["value"] == 1  # Off
    assert parsed["TK"]["value"] == 67.7
    assert parsed["Taus"]["value"] == 5.2
    assert parsed["Lagerstand"]["value"] == 3006
    assert parsed["Verbrauchszähler"]["value"] == 4814

    # No digital channel may be dropped - before digital words were read as
    # hexadecimal, whole words failed to parse and their channels vanished.
    digital = [p for p in parser.parameters if p.is_digital]
    assert len(digital) == len(geometry.digital_channels)
    assert all(p.name in parsed for p in digital)


def test_real_capture_obeys_the_dop_formatting_rules():
    """The template's channel order agrees with how the firmware prints values.

    Two rules hold without exception across the factory recording: a dop='0'
    channel never emits a decimal point, and a dop='2' channel always emits
    exactly two. A misplaced channel shows up here as a violation, which is how
    three misplaced placeholders in this template were found.

    Channels with no dop attribute are deliberately not checked - the boiler
    trims a trailing '.0' on those, so they carry no positional signal.
    """
    geometry = build_geometry(REAL_CAPTURE_FIRMWARE)
    values = REAL_CAPTURE.split()[1:]

    violations = []
    for index in range(geometry.analog_count):
        name, dop = geometry.analog[index]
        token = values[index]
        decimals = len(token.split(".")[1]) if "." in token else 0
        if dop == "0" and decimals != 0:
            violations.append(f"{name} (id {index}) dop='0' but {token!r}")
        elif dop == "2" and decimals != 2:
            violations.append(f"{name} (id {index}) dop='2' but {token!r}")

    assert violations == []


def test_real_capture_matches_manufacturer_signatures():
    """Uninstalled circuits read the same way the manufacturer's own boiler does."""
    geometry = build_geometry(REAL_CAPTURE_FIRMWARE)
    values = REAL_CAPTURE.split()[1:]
    at = {name: values[i] for i, (name, _) in geometry.analog.items()}

    block = ("TVL_{0}", "TVLs_{0}", "TRA_{0}", "TRs_{0}", "HKZustand_{0}", "FR{0} Zustand", "HKP{0} Status")
    circuit_a = [at[part.format("A")] for part in block]
    circuit_b = [at[part.format("B")] for part in block]

    # Neither circuit is installed on this boiler, so both carry the sentinel
    assert circuit_a == circuit_b == ["-20.0", "0", "20.0", "20.0", "0", "1", "0"]

    # Same for the two DHW boilers that are absent
    assert [at["TBA"], at["TBs_A"]] == ["-20.0", "0"]
    assert [at["TBB"], at["TBs_B"]] == ["-20.0", "0"]

    # Wasserdruck is the last analog channel and the only two-decimal value there
    assert geometry.analog[geometry.analog_count - 1][0] == "Wasserdruck"
    assert at["Wasserdruck"] == "0.00"


def test_digital_words_are_read_as_hexadecimal():
    """Digital words are hex, and reading them as decimal changes the result.

    The capture's first digital word is '406'. As hex that is 0x406, setting bits
    1, 2 and 10 - all declared by the template. As decimal it would set bits 1, 2,
    4, 7 and 8, two of which no channel declares.
    """
    parser = HargassnerMessageParser(REAL_CAPTURE_FIRMWARE)
    geometry = build_geometry(REAL_CAPTURE_FIRMWARE)
    parsed = parser.parse_message(REAL_CAPTURE)

    active = {name for name, _, _ in geometry.digital_channels if parsed[name]["value"]}
    assert active == {"Stb", "Fuellstand", "WS freig.", "Aschebox"}

    # The decimal reading would have set two bits the template never declares
    assert 0x406 & ~geometry.declared_mask[0] == 0
    assert 406 & ~geometry.declared_mask[0] != 0


def test_generated_words_with_hex_letters_round_trip():
    """A word containing hex letters parses rather than dropping its channels."""
    parser = HargassnerMessageParser("V14_1HAR_q1")
    geometry = build_geometry("V14_1HAR_q1")

    values = ["0"] * geometry.expected_length
    # Set every declared bit of word 0 - the resulting token contains letters
    values[geometry.analog_count] = format(geometry.declared_mask[0], "X")
    assert any(c in "ABCDEF" for c in values[geometry.analog_count])

    parsed = parser.parse_message("pm " + " ".join(values))

    word0 = [(n, b) for n, w, b in geometry.digital_channels if w == 0]
    assert word0
    for name, _ in word0:
        assert parsed[name]["value"] is True


def test_length_mismatch_warns_once_then_recovers(caplog):
    """A mismatch warns on change, not on every message."""
    parser = HargassnerMessageParser("V14_1HAR_q1")
    short = "pm " + " ".join(["0"] * 50)

    with caplog.at_level(logging.WARNING):
        for _ in range(3):
            parser.parse_message(short)

    warnings = [r for r in caplog.records if "length mismatch" in r.message]
    assert len(warnings) == 1

    caplog.clear()
    good = "pm " + " ".join(["0"] * parser.expected_length)
    with caplog.at_level(logging.INFO):
        parser.parse_message(good)

    assert any("now matches" in r.message for r in caplog.records)


@pytest.mark.parametrize(
    "message,expected",
    [
        ("xy 1 2 3", None),
        ("", None),
        ("not a message at all", None),
    ],
)
def test_rejects_non_pm_messages(message, expected):
    """Anything that is not a pm line is refused."""
    parser = HargassnerMessageParser("V14_1HAR_q1")
    assert parser.parse_message(message) is expected


def test_short_message_parses_what_it_can():
    """A truncated message yields the leading parameters rather than nothing."""
    parser = HargassnerMessageParser("V14_1HAR_q1")

    parsed = parser.parse_message("pm 1 2 3")

    assert parsed == {
        "ZK": {"value": 1, "unit": None, "description": parsed["ZK"]["description"]},
        "O2": {"value": 2, "unit": "%", "description": parsed["O2"]["description"]},
        "O2soll": {"value": 3, "unit": "%", "description": parsed["O2soll"]["description"]},
    }


def test_unknown_firmware_falls_back():
    """An unknown firmware key falls back to the reference template."""
    parser = HargassnerMessageParser("does_not_exist")

    assert parser.expected_length == EXPECTED_LENGTHS["V14_1HAR_q1"]


def test_template_umlauts_survive_import():
    """Template text is genuine UTF-8, not mojibake.

    The DAQ files these templates come from are cp1252; a transcoding slip would
    silently rename entities to things like 'StÃ¶rung'.
    """
    assert "Störungs Nr" in FIRMWARE_TEMPLATES["V14_1HAR_q1"]
    assert "Verbrauchszähler" in FIRMWARE_TEMPLATES["V14_1HAR_q1"]

    parser = HargassnerMessageParser("V14_1HAR_q1")
    assert parser.get_parameter_info("TK").unit == "°C"


def test_last_message_length_is_reported(firmware_key, parser):
    """The parser exposes what it last saw, for template-fit diagnostics."""
    parser.parse_message("pm " + " ".join(["0"] * 30))

    assert parser.last_message_length == 30
    assert parser.expected_length == EXPECTED_LENGTHS[firmware_key]
