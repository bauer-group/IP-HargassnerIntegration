"""Tests for the telnet message parser."""

from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET

import pytest

from conftest import (
    FIRMWARE_TEMPLATES,
    REPO_ROOT,
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

# Telnet lines from a Nano PK Plus on V14.1HAR.q, contributed in Issue #21.
# Seven of the fifteen captured lines: the subset that still reproduces every
# distinct token seen at every position that varies, so it pins the layout as
# tightly as the full capture does. 121 values each.
NANOPKPLUS_CAPTURE = (
    "pm 1 1.1 7.5 28.8 0 29.2 30 10 33.8 0 0 62.7 61.2 42.2 92 5 0 0 0 63 0 0 30.0 100 30 30 76 76.3 92 2 0 0 10 3 0 5 0 7 0 0 6363 0 15063 0.00 0.00 -3 50.2 24107 28.9 117.9 36 -20.0 -20.0 0.0 20.6 20.9 0.0 1 0 -20.0 0 20.0 20.0 0 1 0 28.1 0 20.0 22.0 0 1 0 28.1 0 20.0 20.5 0 1 0 -20.0 0 20.0 20.0 0 1 0 -20.0 0 62.7 0 0 0 -20.0 0 0.0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.00 2 1000 0 0 1 0 0 0",
    "pm 1 1.1 7.5 28.7 0 29.2 30 10 33.7 0 0 62.7 61.2 42.2 92 5 0 0 0 63 0 0 30.0 100 30 30 76 76.3 92 2 0 0 11 3 0 0 0 7 0 0 6363 0 15063 0.00 0.00 -3 50.2 24108 28.8 119.8 36 -20.0 -20.0 0.0 20.6 20.9 0.0 1 0 -20.0 0 20.0 20.0 0 1 0 28.1 0 20.0 22.0 0 1 0 28.1 0 20.0 20.5 0 1 0 -20.0 0 20.0 20.0 0 1 0 -20.0 0 62.8 0 0 0 -20.0 0 0.0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.00 2 0 0 0 1 0 0 0",
    "pm 1 1.1 7.5 28.7 0 29.2 30 10 33.9 0 0 62.7 61.2 42.2 92 5 0 0 0 63 0 0 30.0 100 30 30 76 76.3 92 2 0 0 10 2 0 3 0 7 0 0 6363 0 15063 0.00 0.00 -3 50.2 24107 28.9 117.9 36 -20.0 -20.0 0.0 20.6 20.9 0.0 1 0 -20.0 0 20.0 20.0 0 1 0 28.1 0 20.0 22.0 0 1 0 28.1 0 20.0 20.5 0 1 0 -20.0 0 20.0 20.0 0 1 0 -20.0 0 62.8 0 0 0 -20.0 0 0.0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.00 2 0 0 0 1 0 0 0",
    "pm 1 1.1 7.5 28.8 0 29.2 30 10 34.0 0 0 62.7 61.2 42.1 92 5 0 0 0 63 0 0 30.0 100 30 30 76 76.3 92 2 0 0 11 2 0 0 0 7 0 0 6363 0 15063 0.00 0.00 -3 50.2 24108 28.9 119.8 36 -20.0 -20.0 0.0 20.6 20.9 0.0 1 0 -20.0 0 20.0 20.0 0 1 0 28.2 0 20.0 22.0 0 1 0 28.1 0 20.0 20.5 0 1 0 -20.0 0 20.0 20.0 0 1 0 -20.0 0 62.8 0 0 0 -20.0 0 0.0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.00 2 0 0 0 1 0 0 0",
    "pm 1 1.1 7.5 28.8 0 29.2 30 10 34.1 0 0 62.7 61.2 42.1 92 5 0 0 0 63 0 0 30.0 100 30 30 76 76.3 92 2 0 0 10 3 0 4 0 7 0 0 6363 0 15063 0.00 0.00 -3 50.2 24108 28.8 116.0 36 -20.0 -20.0 0.0 20.6 20.9 0.0 1 0 -20.0 0 20.0 20.0 0 1 0 28.2 0 20.0 22.0 0 1 0 28.1 0 20.0 20.5 0 1 0 -20.0 0 20.0 20.0 0 1 0 -20.0 0 62.8 0 0 0 -20.0 0 0.0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.00 2 1000 0 0 1 0 0 0",
    "pm 1 1.1 7.5 28.7 0 29.2 30 10 34.2 0 0 62.7 61.2 42.1 92 5 0 0 0 63 0 0 30.0 100 30 30 76 76.3 92 2 0 0 11 1 0 4 0 7 0 0 6363 0 15063 0.00 0.00 -3 50.2 24107 28.9 114.2 36 -20.0 -20.0 0.0 20.6 20.9 0.0 1 0 -20.0 0 20.0 20.0 0 1 0 28.2 0 20.0 22.0 0 1 0 28.1 0 20.0 20.5 0 1 0 -20.0 0 20.0 20.0 0 1 0 -20.0 0 62.8 0 0 0 -20.0 0 0.0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.00 2 1000 0 0 1 0 0 0",
    "pm 1 1.1 7.5 28.8 0 29.2 30 10 33.8 0 0 62.7 61.2 42.1 92 5 0 0 0 63 0 0 30.0 100 30 30 76 76.3 92 2 0 0 11 4 0 1 0 7 0 0 6363 0 15063 0.00 0.00 -3 50.2 24107 28.9 116.0 36 -20.0 -20.0 0.0 20.6 20.9 0.0 1 0 -20.0 0 20.0 20.0 0 1 0 28.2 0 20.0 22.0 0 1 0 28.1 0 20.0 20.5 0 1 0 -20.0 0 20.0 20.0 0 1 0 -20.0 0 62.8 0 0 0 -20.0 0 0.0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.00 2 0 0 0 1 0 0 0",
)
NANOPKPLUS_FIRMWARE = "V14_1HAR_q1_nanopkplus"

EXPECTED_LENGTHS = {
    "V14_0HAR_q": 120,
    "V14_0d": 171,
    "V14_0m5": 154,
    "V14_1HAR_q1": 121,
    "V14_1HAR_q1_nano2_32": 120,
    "V14_1HAR_q1_nanopkplus": 121,
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

    assert dop_violations(geometry, REAL_CAPTURE) == []


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


def dop_violations(geometry, message):
    """Positions where a captured token contradicts its channel's dop attribute.

    dop='0' never emits a decimal point and dop='2' always emits exactly two.
    Channels with no dop attribute carry no positional signal - the boiler trims
    a trailing '.0' on those - so they are not checked.
    """
    values = message.split()[1:]
    found = []
    for index in range(geometry.analog_count):
        name, dop = geometry.analog[index]
        token = values[index]
        decimals = len(token.split(".")[1]) if "." in token else 0
        if dop == "0" and decimals != 0:
            found.append(f"{name} (id {index}) dop='0' but {token!r}")
        elif dop == "2" and decimals != 2:
            found.append(f"{name} (id {index}) dop='2' but {token!r}")
    return found


def manufacturer_daq_bytes():
    """The manufacturer's own recording, shipped with the repository."""
    return (REPO_ROOT / "docs" / "private_firmware_samples" / "DAQ00001.DAQ").read_bytes()


def channel_signature(xml):
    """(analog, digital) channel identity of a DAQPRJ, ignoring formatting."""
    root = ET.fromstring(xml)
    analog = [
        (c.get("name"), c.get("unit"), c.get("dop"))
        for c in sorted(root.findall(".//ANALOG/CHANNEL"), key=lambda c: int(c.get("id")))
    ]
    digital = {
        (int(c.get("id")), int(c.get("bit", 0))): c.get("name")
        for c in root.findall(".//DIGITAL/CHANNEL")
    }
    return analog, digital


def test_nano2_32_is_the_manufacturers_own_channel_list():
    """V14_1HAR_q1_nano2_32 is the boiler maker's channel list, verbatim.

    docs/private_firmware_samples/DAQ00001.DAQ is a recording from a Nano.2 32
    whose header reports 'SW=V14.1HAR.q1'. It declares 112 analog + 8 digital
    words = 120 values and orders each heating circuit TVL_x, TVLs_x, TRA_x, TRs_x.

    That is NOT the order V14_1HAR_q1 uses, and both occur in the field under the
    same firmware string - see test_v14_1har_q1_keeps_its_original_layout. This key
    exists so the manufacturer's order is selectable without redefining the other.
    """
    raw = manufacturer_daq_bytes()
    assert b"SW=V14.1HAR.q1" in raw, "sample no longer identifies itself as V14.1HAR.q1"

    daqprj = re.search(rb"<DAQPRJ>.*?</DAQPRJ>", raw, re.S).group(0).decode("cp1252")

    assert (channel_signature(FIRMWARE_TEMPLATES["V14_1HAR_q1_nano2_32"])
            == channel_signature(daqprj))
    assert HargassnerMessageParser("V14_1HAR_q1_nano2_32").expected_length == 120


def test_v14_1har_q1_keeps_its_original_layout():
    """V14_1HAR_q1 must keep the layout it has had since the first release.

    It differs from the manufacturer's DAQ (TRA_x ahead of TVL_x, TBs_1 before
    TB1, a ninth digital word Reserved_8), and for a while that looked simply
    wrong. It is not: an HG-PK32 in the field reads plausible heating-circuit
    values with THIS order and implausible ones with the manufacturer's, so both
    orders exist under one firmware string. The manufacturer's order lives in
    V14_1HAR_q1_nano2_32.

    Redefining this key moves values between entities on every installation
    already using it - which is what v0.5.0 did and v0.5.1 reverted. The layout
    is pinned here deliberately: if it ever needs to change, it gets a new key.
    """
    analog, digital = channel_signature(FIRMWARE_TEMPLATES["V14_1HAR_q1"])
    names = [name for name, _, _ in analog]

    for circuit in ("A", "1", "2", "B"):
        assert names.index(f"TRA_{circuit}") < names.index(f"TVL_{circuit}")
    assert names.index("TBs_1") < names.index("TB1")
    assert digital.get((8, 0)) == "Reserved_8"
    assert digital.get((5, 0)) == "Reserved_5"
    assert HargassnerMessageParser("V14_1HAR_q1").expected_length == 121


def test_nanopkplus_capture_parses_completely():
    """Every captured line yields every parameter the variant declares."""
    parser = HargassnerMessageParser(NANOPKPLUS_FIRMWARE)

    assert parser.expected_length == 121

    for message in NANOPKPLUS_CAPTURE:
        assert len(message.split()) - 1 == 121
        parsed = parser.parse_message(message)
        assert parsed is not None
        assert [p.name for p in parser.parameters if p.name not in parsed] == []

    parsed = parser.parse_message(NANOPKPLUS_CAPTURE[0])

    # Readings the reporter could confirm against the boiler display
    assert parsed["ZK"]["value"] == 1  # Off
    assert parsed["TK"]["value"] == 28.8
    assert parsed["TPo"]["value"] == 62.7
    assert parsed["Verbrauchszähler"]["value"] == 15063

    # The channel that made the misalignment visible: read two positions early,
    # the 24 V supply rail appeared as a ~24000 °C burner temperature (issue #22)
    assert parsed["U Netzteil"]["value"] == 24107
    assert parsed["U Netzteil"]["unit"] == "mV"
    assert parsed["BRT"]["value"] == 117.9


def test_nanopkplus_capture_obeys_the_dop_formatting_rules():
    """The variant's channel order agrees with how this boiler prints values."""
    geometry = build_geometry(NANOPKPLUS_FIRMWARE)

    assert {m: v for m in NANOPKPLUS_CAPTURE if (v := dop_violations(geometry, m))} == {}


def test_nanopkplus_matches_manufacturer_signatures():
    """Uninstalled circuits and boilers read the way the factory recording does."""
    geometry = build_geometry(NANOPKPLUS_FIRMWARE)
    values = NANOPKPLUS_CAPTURE[0].split()[1:]
    at = {name: values[i] for i, (name, _) in geometry.analog.items()}

    block = ("TVL_{0}", "TVLs_{0}", "TRA_{0}", "TRs_{0}", "HKZustand_{0}",
             "FR{0} Zustand", "HKP{0} Status")
    sentinel = ["-20.0", "0", "20.0", "20.0", "0", "1", "0"]

    # A and B are not installed on this boiler and carry the factory sentinel
    assert [at[part.format("A")] for part in block] == sentinel
    assert [at[part.format("B")] for part in block] == sentinel

    # 1 and 2 are installed, so they must not read as the sentinel
    assert [at[part.format("1")] for part in block] != sentinel
    assert [at[part.format("2")] for part in block] != sentinel

    # DHW boilers A and B absent, boiler 1 present
    assert [at["TBA"], at["TBs_A"]] == ["-20.0", "0"]
    assert [at["TBB"], at["TBs_B"]] == ["-20.0", "0"]
    assert at["TB1"] == "62.7"

    # Wasserdruck is the last analog channel and the only two-decimal value there
    assert geometry.analog[geometry.analog_count - 1][0] == "Wasserdruck"
    assert at["Wasserdruck"] == "0.00"


def test_nanopkplus_digital_words_set_only_declared_bits():
    """No captured word sets a bit no channel claims.

    A word that sets an undeclared bit is the signature of a wrong analog/digital
    split: the stock V14_1HAR_q1 read this boiler's last analog value ('0.00') as
    its first digital word, which is not even valid hexadecimal.
    """
    geometry = build_geometry(NANOPKPLUS_FIRMWARE)

    for message in NANOPKPLUS_CAPTURE:
        words = message.split()[1:][geometry.analog_count:]
        assert len(words) == geometry.digital_word_count
        for index, token in enumerate(words):
            undeclared = int(token, 16) & ~geometry.declared_mask.get(index, 0)
            assert undeclared == 0, (
                f"word {index} = {token!r} sets undeclared bits {undeclared:#x}"
            )
