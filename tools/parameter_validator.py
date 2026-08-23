#!/usr/bin/env python3
"""Parameter Consistency Validator for Hargassner Integration.

Validates that firmware templates and parameter descriptions are consistent.

Usage:
    python parameter_validator.py [--fix] [--verbose]

Examples:
    python parameter_validator.py
    python parameter_validator.py --verbose
    python parameter_validator.py --fix
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from _integration_import import load_module

    _templates = load_module("firmware_templates")
    FIRMWARE_TEMPLATES = _templates.FIRMWARE_TEMPLATES
    PARAMETER_DESCRIPTIONS = _templates.PARAMETER_DESCRIPTIONS
    HargassnerMessageParser = load_module("message_parser").HargassnerMessageParser
except (ImportError, FileNotFoundError) as err:
    print(f"Error: Could not import firmware templates: {err}", file=sys.stderr)
    print("Make sure the integration is in the correct directory structure", file=sys.stderr)
    sys.exit(1)


def _is_placeholder(name: str) -> bool:
    """Return True for reserved-position channels that carry no value."""
    return name.lower().startswith("dummy")


class ParameterValidator:
    """Validate parameter consistency across firmware templates."""

    def __init__(self, verbose: bool = False):
        """Initialize validator.

        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

    def validate(self) -> bool:
        """Run all validation checks.

        Returns:
            True if all checks passed
        """
        print("=" * 70)
        print("PARAMETER VALIDATION")
        print("=" * 70)
        print()

        # 1. Check template parsing
        self._check_template_parsing()

        # 2. Extract all parameters
        all_params = self._extract_all_parameters()

        # 3. Check parameter descriptions
        self._check_parameter_descriptions(all_params)

        # 4. Check for duplicates
        self._check_duplicates()

        # 5. Check parameter naming conventions
        self._check_naming_conventions(all_params)

        # Print results
        self._print_results()

        return len(self.errors) == 0

    def _check_template_parsing(self):
        """Check that all templates can be parsed."""
        print("Checking template parsing...")

        for firmware, template in FIRMWARE_TEMPLATES.items():
            try:
                parser = HargassnerMessageParser(firmware)
                param_count = len(parser.parameters)

                analog_count = sum(1 for p in parser.parameters if not p.is_digital)
                digital_count = sum(1 for p in parser.parameters if p.is_digital)

                self.info.append(
                    f"[OK] {firmware}: {param_count} parameters "
                    f"({analog_count} analog, {digital_count} digital)"
                )

            except Exception as e:
                self.errors.append(f"[ERROR] {firmware}: Failed to parse template: {e}")

    def _extract_all_parameters(self) -> Set[str]:
        """Extract all parameter names from templates.

        Returns:
            Set of all parameter names
        """
        all_params = set()

        for firmware, template in FIRMWARE_TEMPLATES.items():
            try:
                parser = HargassnerMessageParser(firmware)
                for param in parser.parameters:
                    all_params.add(param.name)
            except Exception:
                pass

        return all_params

    def _check_parameter_descriptions(self, all_params: Set[str]):
        """Check parameter descriptions coverage.

        Args:
            all_params: Set of all parameter names
        """
        print("Checking parameter descriptions...")

        described_params = set(PARAMETER_DESCRIPTIONS.keys())

        # Parameters without descriptions
        missing_descriptions = all_params - described_params
        if missing_descriptions:
            self.warnings.append(
                f"[WARN] {len(missing_descriptions)} parameters without descriptions:"
            )
            for param in sorted(missing_descriptions):
                self.warnings.append(f"    - {param}")

        # Descriptions for non-existent parameters
        extra_descriptions = described_params - all_params
        if extra_descriptions:
            self.warnings.append(
                f"[WARN] {len(extra_descriptions)} descriptions for non-existent parameters:"
            )
            for param in sorted(extra_descriptions):
                self.warnings.append(f"    - {param}")

        # Coverage statistics
        coverage = (len(described_params & all_params) / len(all_params) * 100) if all_params else 0
        self.info.append(f"[STAT] Description coverage: {coverage:.1f}% ({len(described_params & all_params)}/{len(all_params)})")

    def _check_duplicates(self):
        """Check for duplicate parameter names within templates.

        Reads the XML directly: the parser keys its parameters by name, so any
        collision has already silently overwritten the earlier channel by the
        time ``parser.parameters`` is available.
        """
        print("Checking for duplicates...")

        for firmware, template in FIRMWARE_TEMPLATES.items():
            try:
                root = ET.fromstring(template)
            except ET.ParseError:
                continue  # already reported by _check_template_parsing

            for section in ("ANALOG", "DIGITAL"):
                names = [
                    channel.get("name")
                    for channel in root.findall(f".//{section}/CHANNEL")
                ]

                seen: Set[str] = set()
                duplicates: Set[str] = set()
                for name in names:
                    if name in seen:
                        duplicates.add(name)
                    seen.add(name)

                if not duplicates:
                    continue

                # Placeholder channels are expected to repeat - they only reserve
                # a position in the message and carry no value of their own
                real = sorted(d for d in duplicates if not _is_placeholder(d))
                padding = sorted(d for d in duplicates if _is_placeholder(d))

                if real:
                    self.errors.append(
                        f"[ERROR] {firmware}: Duplicate {section.lower()} parameters "
                        f"(later channel overwrites earlier): {', '.join(real)}"
                    )
                if padding:
                    self.warnings.append(
                        f"[WARN] {firmware}: Duplicate {section.lower()} placeholder "
                        f"names collapse into one entity: {', '.join(padding)}"
                    )

    def _check_naming_conventions(self, all_params: Set[str]):
        """Check parameter naming conventions.

        Args:
            all_params: Set of all parameter names
        """
        print("Checking naming conventions...")

        suspicious_names = []

        for param in all_params:
            # Check for suspicious patterns
            if param.strip() != param:
                suspicious_names.append(f"{param!r} (leading/trailing whitespace)")
            elif "  " in param:
                suspicious_names.append(f"{param!r} (double spaces)")
            elif param.lower() == param and len(param) > 3:
                # Might be inconsistent casing
                suspicious_names.append(f"{param!r} (all lowercase)")

        if suspicious_names:
            self.warnings.append(
                f"[WARN] {len(suspicious_names)} parameters with suspicious names:"
            )
            for name in suspicious_names[:10]:  # Limit output
                self.warnings.append(f"    - {name}")
            if len(suspicious_names) > 10:
                self.warnings.append(f"    ... and {len(suspicious_names) - 10} more")

    def _print_results(self):
        """Print validation results."""
        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print()

        # Info messages
        if self.info and self.verbose:
            print("INFO:")
            for msg in self.info:
                self._safe_print(f"  {msg}")
            print()

        # Warnings
        if self.warnings:
            print("WARNINGS:")
            for msg in self.warnings:
                self._safe_print(f"  {msg}")
            print()

        # Errors
        if self.errors:
            print("ERRORS:")
            for msg in self.errors:
                self._safe_print(f"  {msg}")
            print()

        # Summary
        print("SUMMARY:")
        print(f"  Errors:   {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")

        if len(self.errors) == 0 and len(self.warnings) == 0:
            print("\n[OK] All checks passed!")
        elif len(self.errors) == 0:
            print("\n[WARN] Validation passed with warnings")
        else:
            print("\n[FAIL] Validation failed")

    def _safe_print(self, text: str):
        """Print text with encoding fallback for Windows console.

        Args:
            text: Text to print
        """
        try:
            print(text)
        except UnicodeEncodeError:
            print(text.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate parameter consistency for Hargassner integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python parameter_validator.py
  python parameter_validator.py --verbose
        """,
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Create validator
    validator = ParameterValidator(verbose=args.verbose)

    # Run validation
    success = validator.validate()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
