#!/usr/bin/env python3
"""Test Message Generator for Hargassner Integration.

Generates realistic test messages for development and testing purposes.

Usage:
    python message_generator.py [--firmware <version>] [--count <n>] [--format <format>]

Examples:
    python message_generator.py
    python message_generator.py --count 5
    python message_generator.py --firmware V14_1HAR_q1 --format json
"""

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from _integration_import import load_module

    FIRMWARE_TEMPLATES = load_module("firmware_templates").FIRMWARE_TEMPLATES
    HargassnerMessageParser = load_module("message_parser").HargassnerMessageParser
except (ImportError, FileNotFoundError) as err:
    print(f"Error: Could not import firmware templates: {err}", file=sys.stderr)
    print("Make sure the integration is in the correct directory structure", file=sys.stderr)
    sys.exit(1)


class MessageGenerator:
    """Generate realistic test messages for Hargassner boilers."""

    def __init__(self, firmware: str = "V14_1HAR_q1"):
        """Initialize generator.

        Args:
            firmware: Firmware version to generate messages for
        """
        self.firmware = firmware

        if firmware not in FIRMWARE_TEMPLATES:
            raise ValueError(f"Unknown firmware: {firmware}")

        # Parse template to get parameter structure
        self.parser = HargassnerMessageParser(firmware)
        self.param_count = len(self.parser.parameters)

        # Realistic value ranges for common parameters
        self.value_ranges = {
            "ZK": (0, 12),  # Boiler state
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
        }

    def generate_realistic_value(self, param_name: str) -> float:
        """Generate realistic value for a parameter.

        Args:
            param_name: Parameter name

        Returns:
            Generated value
        """
        # Check if we have a specific range
        if param_name in self.value_ranges:
            min_val, max_val = self.value_ranges[param_name]
            return round(random.uniform(min_val, max_val), 1)

        # Default ranges based on common patterns
        if "temp" in param_name.lower() or param_name.startswith("T"):
            return round(random.uniform(20.0, 80.0), 1)
        elif "%" in param_name or "soll" in param_name.lower():
            return round(random.uniform(0.0, 100.0), 1)
        elif "Anf" in param_name:
            return round(random.uniform(0.0, 80.0), 1)
        else:
            return round(random.uniform(0.0, 100.0), 1)

    def generate_message(self, state: str = "running") -> str:
        """Generate a realistic pm message.

        Args:
            state: Boiler state - "off", "starting", "running", "cooling"

        Returns:
            Generated pm message string
        """
        values = []

        # Get analog parameters only (digital are packed separately)
        analog_params = [p for p in self.parser.parameters if hasattr(p, 'is_digital') and not p.is_digital]

        # Handle case where parameters is a list of strings (parameter names)
        if analog_params and isinstance(analog_params[0], str):
            analog_params = [{'name': p} for p in analog_params]

        for i, param in enumerate(analog_params):
            param_name = param.name if hasattr(param, 'name') else param.get('name', f'param_{i}')

            if False:  # Digital params handled separately
                pass  # Not used
            else:
                # Generate based on parameter name
                if param_name == "ZK":  # Boiler state
                    if state == "off":
                        values.append("1")  # Off
                    elif state == "starting":
                        values.append(str(random.randint(2, 6)))  # Starting states
                    elif state == "running":
                        values.append("7")  # Full firing
                    else:  # cooling
                        values.append("8")  # Ember preservation
                elif param_name in self.value_ranges:
                    val = self.generate_realistic_value(param_name)
                    values.append(str(val))
                else:
                    val = self.generate_realistic_value(param_name)
                    values.append(str(val))

        # Add digital parameter values (packed as integers)
        digital_count = sum(1 for p in self.parser.parameters if hasattr(p, 'is_digital') and p.is_digital)
        if digital_count > 0:
            # Add some random digital values
            for _ in range(max(2, (digital_count + 7) // 8)):  # Estimate number of digital integers
                values.append(str(random.randint(0, 255)))

        return "pm " + " ".join(values)

    def generate_messages(self, count: int = 1, vary_state: bool = True) -> List[str]:
        """Generate multiple messages.

        Args:
            count: Number of messages to generate
            vary_state: Whether to vary boiler state

        Returns:
            List of generated messages
        """
        messages = []
        states = ["running", "running", "running", "starting", "off"]  # Weighted towards running

        for i in range(count):
            if vary_state:
                state = random.choice(states)
            else:
                state = "running"

            msg = self.generate_message(state)
            messages.append(msg)

        return messages


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate test messages for Hargassner integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python message_generator.py
  python message_generator.py --count 5
  python message_generator.py --firmware V14_1HAR_q1 --format json
  python message_generator.py --count 10 --no-vary > test_messages.txt
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
        "--format",
        "-o",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--no-vary",
        action="store_true",
        help="Don't vary boiler state (always running)",
    )

    args = parser.parse_args()

    # Create generator
    try:
        generator = MessageGenerator(args.firmware)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate messages
    messages = generator.generate_messages(args.count, vary_state=not args.no_vary)

    # Output
    if args.format == "json":
        output = {
            "firmware": args.firmware,
            "parameter_count": generator.param_count,
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
