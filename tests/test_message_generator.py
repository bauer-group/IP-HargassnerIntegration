"""Tests for the test-message generator.

The generator and the parser are two independent readings of the same DAQPRJ
template. These tests pin the generator's output against the layout read from the
XML directly, then round-trip it through the parser.
"""

from __future__ import annotations

import logging
import re
import subprocess
import sys

import pytest

from conftest import (
    BOILER_STATES,
    REPO_ROOT,
    MessageGenerator,
    build_geometry,
)

VALUE_TOKEN = re.compile(r"^-?[0-9A-F]+(\.[0-9]+)?$")
HEX_WORD = re.compile(r"^[0-9A-F]+$")

# Protocol lengths, pinned. A template edit that shifts one of these has to show up
# as a deliberate diff here rather than silently changing what the boiler must send.
EXPECTED_LENGTHS = {
    "V14_0HAR_q": 120,
    "V14_0d": 171,
    "V14_0m5": 154,
    "V14_1HAR_q1": 121,
    "V14_1HAR_q1_solar": 140,
    "V14_1HAR_q_nano2_zuspuf_aup3": 155,
    "V40_0HAR_az15": 157,
}


def tokens(message: str) -> list[str]:
    """Split a pm message into its values."""
    return message.split()[1:]


def test_length_matches_template(generator, geometry, parser, firmware_key):
    """A generated message carries exactly the value count the template implies."""
    values = tokens(generator.generate_message("heating"))

    assert len(values) == geometry.expected_length
    assert len(values) == parser.expected_length
    assert len(values) == EXPECTED_LENGTHS[firmware_key]


def test_message_is_well_formed(generator):
    """Output matches the shape of a real telnet line."""
    message = generator.generate_message("heating")

    assert message.startswith("pm ")
    assert message == message.strip()
    assert "  " not in message
    for value in tokens(message):
        assert VALUE_TOKEN.match(value), f"malformed token: {value!r}"


def test_analog_decimals_match_dop(generator, geometry):
    """Each analog value carries the decimal places its dop attribute declares."""
    values = tokens(generator.generate_message("heating"))

    for index in range(geometry.analog_count):
        _, dop = geometry.analog[index]
        want = 1 if dop is None else int(dop)
        token = values[index]
        got = len(token.split(".")[1]) if "." in token else 0
        assert got == want, f"index {index}: dop={dop} produced {token!r}"


def test_digital_words_are_uppercase_hex_of_declared_bits(generator, geometry):
    """Digital words are bare uppercase hex and never set an undeclared bit."""
    values = tokens(generator.generate_message("heating"))

    for word_id in range(geometry.digital_word_count):
        token = values[geometry.analog_count + word_id]

        assert HEX_WORD.match(token), f"word {word_id} is not bare uppercase hex: {token!r}"
        assert token == "0" or not token.startswith("0"), f"word {word_id} zero-padded"

        value = int(token, 16)
        assert value < 1 << 32
        undeclared = value & ~geometry.declared_mask.get(word_id, 0)
        assert undeclared == 0, f"word {word_id} sets undeclared bits {undeclared:#x}"


def test_exact_round_trip(generator, geometry, parser):
    """Every emitted value comes back out of the parser unchanged.

    Ground truth is the emitted text, not the generator's internals - so this
    fails if either side drifts.
    """
    message = generator.generate_message("heating")
    values = tokens(message)
    parsed = parser.parse_message(message)

    assert parsed is not None

    # Names repeated across channels collapse in the parser's name-keyed dict, so
    # only the last id for such a name is observable.
    last_id_for_name: dict[str, int] = {}
    for index in range(geometry.analog_count):
        name, _ = geometry.analog[index]
        last_id_for_name[name] = index

    for index in range(geometry.analog_count):
        name, _ = geometry.analog[index]
        if last_id_for_name[name] != index:
            continue
        token = values[index]
        want = float(token) if "." in token else int(token)
        assert parsed[name]["value"] == want, f"analog {name!r} at {index}"

    for name, word_id, bit in geometry.digital_channels:
        word = int(values[geometry.analog_count + word_id], 16)
        assert parsed[name]["value"] is bool(word >> bit & 1), f"digital {name!r}"

    missing = [p.name for p in parser.parameters if p.name not in parsed]
    assert missing == []


@pytest.mark.parametrize(
    "firmware_key",
    ["V14_0HAR_q", "V14_1HAR_q1_solar", "V14_1HAR_q_nano2_zuspuf_aup3"],
)
def test_undeclared_word_still_occupies_its_slot(firmware_key):
    """A word id no channel declares is still emitted, as '0'.

    These templates declare digital word ids 0-4, 6 and 7. Word 5 has no channels
    but still takes up a position, and a real capture carries '0' there.
    """
    geometry = build_geometry(firmware_key)
    assert 5 not in geometry.declared_mask

    values = tokens(MessageGenerator(firmware_key, seed=1).generate_message("heating"))

    assert values[geometry.analog_count + 5] == "0"
    assert len(values) == EXPECTED_LENGTHS[firmware_key]


def test_duplicate_names_keep_their_slots():
    """Repeated channel names each keep their own position.

    V14_0m5 names seven separate channels 'DUMMY'. A generator that worked from
    parameter names rather than channel ids would emit six values too few.
    """
    geometry = build_geometry("V14_0m5")
    names = [geometry.analog[i][0] for i in range(geometry.analog_count)]

    assert names.count("DUMMY") == 7
    assert len(set(names)) < geometry.analog_count

    values = tokens(MessageGenerator("V14_0m5", seed=1).generate_message("heating"))
    assert len(values) - geometry.digital_word_count == geometry.analog_count == 146


@pytest.mark.parametrize("state", sorted(BOILER_STATES))
def test_zk_matches_state(generator, parser, state):
    """The boiler-state parameter reflects the requested state."""
    parsed = parser.parse_message(generator.generate_message(state))

    assert int(parsed["ZK"]["value"]) == BOILER_STATES[state]


def test_zk_is_located_by_name_not_position():
    """ZK is not at index 0 on every firmware.

    V40_0HAR_az15 puts Programm first and ZK at index 2, so a generator that
    hardcoded position 0 would write the state into the wrong channel.
    """
    parser_az = MessageGenerator("V40_0HAR_az15", seed=1).parser
    assert parser_az.get_parameter_info("ZK").index == 2

    parsed = parser_az.parse_message(
        MessageGenerator("V40_0HAR_az15", seed=1).generate_message("heating")
    )
    assert int(parsed["ZK"]["value"]) == BOILER_STATES["heating"]


def test_unknown_state_is_rejected(generator):
    """An unsupported state name fails loudly."""
    with pytest.raises(ValueError, match="Unknown state"):
        generator.generate_message("running")


def test_unknown_firmware_is_rejected():
    """An unsupported firmware key fails loudly."""
    with pytest.raises(ValueError, match="Unknown firmware"):
        MessageGenerator("V99_nonexistent")


def test_seed_is_deterministic(firmware_key):
    """The same seed reproduces the same messages, a different seed does not."""
    first = MessageGenerator(firmware_key, seed=42).generate_messages(3, state="heating")
    again = MessageGenerator(firmware_key, seed=42).generate_messages(3, state="heating")
    other = MessageGenerator(firmware_key, seed=43).generate_messages(3, state="heating")

    assert first == again
    assert first != other


def test_no_length_warning_logged(generator, parser, caplog):
    """Parsing a generated message does not trip the template-mismatch warning."""
    message = generator.generate_message("heating")

    with caplog.at_level(logging.WARNING):
        parser.parse_message(message)

    assert "length mismatch" not in caplog.text


@pytest.mark.parametrize("output_format", ["text", "json"])
def test_cli_smoke(output_format):
    """The command line runs and emits messages of the right length."""
    result = subprocess.run(
        [
            sys.executable,
            "tools/message_generator.py",
            "--firmware", "V40_0HAR_az15",
            "--count", "3",
            "--state", "heating",
            "--seed", "1",
            "--format", output_format,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    if output_format == "json":
        import json

        data = json.loads(result.stdout)
        assert data["expected_length"] == 157
        messages = data["messages"]
    else:
        messages = [ln for ln in result.stdout.splitlines() if ln.startswith("pm ")]

    assert len(messages) == 3
    for message in messages:
        assert len(tokens(message)) == 157
