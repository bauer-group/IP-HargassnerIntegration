#!/usr/bin/env python3
"""Test Message Generator for Hargassner Integration.

Generates protocol-valid test messages from a firmware template, for development
and testing without a real boiler.

The output is built from the DAQPRJ template itself, so a generated message always
has exactly the value count the parser expects for that firmware:

    analog block   positions 0..N-1, one per ANALOG CHANNEL id
    digital block  N following words, each packing the DIGITAL CHANNEL bits of one id

Usage:
    python message_generator.py [--firmware <version>] [--count <n>]
                                [--state <state>] [--format <format>] [--seed <n>]

Examples:
    python message_generator.py
    python message_generator.py --count 5
    python message_generator.py --firmware V14_1HAR_q1 --format json
"""

import argparse
import json
import random
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from _integration_import import load_module

    FIRMWARE_TEMPLATES = load_module("firmware_templates").FIRMWARE_TEMPLATES
    HargassnerMessageParser = load_module("message_parser").HargassnerMessageParser
except (ImportError, FileNotFoundError) as err:
    print(f"Error: Could not import firmware templates: {err}", file=sys.stderr)
    print("Make sure the integration is in the correct directory structure", file=sys.stderr)
    sys.exit(1)


# Boiler states, as ZK values. Names match the documented --state choices; the
# integers are the indices into BOILER_STATES_EN/DE in const.py.
BOILER_STATES: Dict[str, int] = {
    "off": 1,
    "ignition": 5,
    "heating": 7,
    "cleaning": 12,
}

# How likely a defined digital bit is set, per state. Only a plausibility knob -
# a boiler that is off has few active outputs, one at full firing has many.
_BIT_DENSITY: Dict[str, float] = {
    "off": 0.10,
    "ignition": 0.40,
    "heating": 0.55,
    "cleaning": 0.35,
}

# Channels whose name starts with this only reserve a position in the message
_PLACEHOLDER_PREFIX = "dummy"


class MessageGenerator:
    """Generate protocol-valid test messages for Hargassner boilers."""

    def __init__(self, firmware: str = "V14_1HAR_q1", seed: Optional[int] = None) -> None:
        """Initialize generator.

        Args:
            firmware: Firmware version to generate messages for
            seed: Optional RNG seed, for reproducible output in tests

        Raises:
            ValueError: If the firmware key is unknown or the template is inconsistent
        """
        if firmware not in FIRMWARE_TEMPLATES:
            raise ValueError(f"Unknown firmware: {firmware}")

        self.firmware = firmware
        self._random = random.Random(seed)

        root = ET.fromstring(FIRMWARE_TEMPLATES[firmware])

        # Analog channels keyed by id - the id IS the position in the message, so
        # this must not be keyed by name: V14_0m5 reuses the name "DUMMY" for seven
        # separate channels, and a name-keyed structure would silently lose six.
        self._analog: Dict[int, Tuple[str, Optional[str]]] = {}
        for channel in root.findall(".//ANALOG/CHANNEL"):
            self._analog[int(channel.get("id"))] = (
                channel.get("name", ""),
                channel.get("dop"),
            )

        # Digital channels grouped into the words they are packed into
        self._digital_bits: Dict[int, List[int]] = defaultdict(list)
        for channel in root.findall(".//DIGITAL/CHANNEL"):
            self._digital_bits[int(channel.get("id"))].append(int(channel.get("bit", 0)))

        self.analog_count = max(self._analog) + 1 if self._analog else 0
        self.digital_word_count = max(self._digital_bits) + 1 if self._digital_bits else 0

        self.parser = HargassnerMessageParser(firmware)
        self.param_count = len(self.parser.parameters)

        # The generator derives its length the same way the parser does. If these
        # ever disagree, the template is malformed - fail loudly rather than emit
        # messages that look valid but are not.
        if self.analog_count + self.digital_word_count != self.parser.expected_length:
            raise ValueError(
                f"Template {firmware} is inconsistent: "
                f"{self.analog_count} analog + {self.digital_word_count} digital words "
                f"!= parser expected_length {self.parser.expected_length}"
            )

        self.expected_length = self.parser.expected_length

        # Realistic value ranges for well-known parameters
        self.value_ranges: Dict[str, Tuple[float, float]] = {
            "O2": (0.0, 21.0),  # O2 percentage
            "TK": (20.0, 90.0),  # Boiler temp
            "TKsoll": (50.0, 85.0),  # Target temp
            "TRL": (20.0, 70.0),  # Return temp
            "TRG": (50.0, 250.0),  # Smoke gas temp
            "SZist": (0.0, 100.0),  # Draft current
            "SZsoll": (0.0, 100.0),  # Draft target
            "TPo": (20.0, 90.0),  # Buffer top
            "TPm": (20.0, 80.0),  # Buffer middle
            "TPu": (20.0, 70.0),  # Buffer bottom
            "Leistung": (0.0, 100.0),  # Output power
            "ESsoll": (0.0, 100.0),  # Delivery rate
            "Taus": (-20.0, 40.0),  # Outside temp
            "Lagerstand": (0.0, 5000.0),  # Pellet stock (kg)
            "Verbrauchszähler": (0.0, 50000.0),  # Consumption (kg)
            "Verbrauchszaehler": (0.0, 50000.0),  # ASCII-normalized variant
        }

    def generate_realistic_value(self, param_name: str) -> float:
        """Generate a plausible value for a parameter.

        Args:
            param_name: Parameter name from the template

        Returns:
            Generated value
        """
        if param_name in self.value_ranges:
            low, high = self.value_ranges[param_name]
            return self._random.uniform(low, high)

        # Fall back to ranges inferred from the name
        if "temp" in param_name.lower() or param_name.startswith("T"):
            return self._random.uniform(20.0, 80.0)
        if "soll" in param_name.lower() or "Anf" in param_name:
            return self._random.uniform(0.0, 80.0)
        return self._random.uniform(0.0, 100.0)

    @staticmethod
    def format_value(value: float, dop: Optional[str]) -> str:
        """Render a value the way the boiler renders it.

        The DAQPRJ 'dop' attribute carries the number of decimal places the channel
        is displayed with, and the telnet stream follows it without exception:
        dop='0' never emits a decimal point, dop='2' always emits exactly two.

        Channels with no dop attribute are looser - the boiler emits one decimal but
        sometimes trims a trailing '.0', so the same channel can print '30.1' and
        '30' on consecutive messages. One decimal is always well-formed, so it is
        emitted unconditionally rather than trying to reproduce the trimming.

        Args:
            value: Numeric value
            dop: Value of the channel's dop attribute, or None if absent

        Returns:
            Formatted value
        """
        try:
            decimals = int(dop) if dop is not None else 1
        except ValueError:
            decimals = 1
        return f"{value:.{max(decimals, 0)}f}"

    def _analog_value(self, index: int, state: str) -> str:
        """Build one analog value for the given message position."""
        name, dop = self._analog.get(index, ("", "0"))

        # A position the template does not describe still has to be filled, or every
        # later index shifts. Emit a neutral zero.
        if not name:
            return self.format_value(0.0, dop)

        if name == "ZK":
            return self.format_value(float(BOILER_STATES[state]), dop)

        if name.lower().startswith(_PLACEHOLDER_PREFIX):
            return self.format_value(0.0, dop)

        return self.format_value(self.generate_realistic_value(name), dop)

    def _digital_word(self, word_id: int, state: str) -> str:
        """Pack one digital word.

        Only bits the template actually defines are ever set, so a generated message
        round-trips: parsing it back yields exactly the booleans that were packed,
        with no phantom channels.

        Words are emitted as uppercase hexadecimal without prefix or padding, which
        is how the boiler emits them ('E', '21', '2007').
        """
        density = _BIT_DENSITY[state]
        word = 0
        for bit in self._digital_bits.get(word_id, []):
            if self._random.random() < density:
                word |= 1 << bit
        return format(word, "X")

    def generate_message(self, state: str = "heating") -> str:
        """Generate one pm message.

        Args:
            state: Boiler state - one of BOILER_STATES

        Returns:
            Generated pm message string

        Raises:
            ValueError: If the state is unknown
        """
        if state not in BOILER_STATES:
            raise ValueError(
                f"Unknown state: {state} (expected one of {', '.join(BOILER_STATES)})"
            )

        values = [self._analog_value(i, state) for i in range(self.analog_count)]
        values += [self._digital_word(w, state) for w in range(self.digital_word_count)]

        return "pm " + " ".join(values)

    def generate_messages(
        self, count: int = 1, state: Optional[str] = None
    ) -> List[str]:
        """Generate multiple messages.

        Args:
            count: Number of messages to generate
            state: Fixed boiler state, or None to vary across messages

        Returns:
            List of generated messages
        """
        # Weighted towards heating - that is where most parameters carry signal
        rotation = ["heating", "heating", "heating", "ignition", "cleaning", "off"]

        return [
            self.generate_message(state or self._random.choice(rotation))
            for _ in range(count)
        ]


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate test messages for Hargassner integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python message_generator.py
  python message_generator.py --count 5
  python message_generator.py --firmware V14_1HAR_q1 --format json
  python message_generator.py --count 10 --state heating > test_messages.txt
        """,
    )

    parser.add_argument(
        "--firmware",
        "-f",
        default="V14_1HAR_q1",
        choices=list(FIRMWARE_TEMPLATES.keys()),
        help="Firmware version (default: V14_1HAR_q1)",
    )
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=1,
        help="Number of messages to generate (default: 1)",
    )
    parser.add_argument(
        "--state",
        "-s",
        choices=list(BOILER_STATES),
        default=None,
        help="Boiler state (default: vary across messages)",
    )
    parser.add_argument(
        "--format",
        "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="RNG seed, for reproducible output",
    )

    args = parser.parse_args()

    try:
        generator = MessageGenerator(args.firmware, seed=args.seed)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    messages = generator.generate_messages(args.count, state=args.state)

    if args.format == "json":
        output = {
            "firmware": args.firmware,
            "parameter_count": generator.param_count,
            "expected_length": generator.expected_length,
            "generated_at": datetime.now().isoformat(),
            "messages": messages,
        }
        print(json.dumps(output, indent=2))
    else:
        for i, msg in enumerate(messages, 1):
            print(f"# Message {i}")
            print(msg)
            if i < len(messages):
                print()


if __name__ == "__main__":
    main()
