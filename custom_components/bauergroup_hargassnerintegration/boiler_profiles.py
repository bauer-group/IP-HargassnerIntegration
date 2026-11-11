"""Boiler profiles: everything that differs between Hargassner boiler families.

The firmware template decides which channels a boiler sends. The profile decides
how those channels are presented: names of the ZK states, the meaning of the
fault numbers, which channels make up the STANDARD sensor set, how heat energy
is derived, and the device model shown in Home Assistant.

This module is pure Python (no Home Assistant imports) so tests and the
developer tools can load it directly. Device and state classes are kept as the
plain strings Home Assistant's enums are built from ("temperature",
"measurement", ...); sensor.py converts them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from .const import (
    BOILER_STATES_DE,
    BOILER_STATES_EN,
    BOILER_TYPE_LOG_WOOD,
    BOILER_TYPE_PELLET,
    ERROR_CODES,
)

# Energy sensor kinds
ENERGY_PELLET_CONSUMPTION: Final = "pellet_consumption"
ENERGY_BUFFER_STORED: Final = "buffer_stored"

# (parameter key, fallback name, device class, state class, icon)
SensorSpec = tuple[str, str, "str | None", "str | None", "str | None"]

_T = "temperature"
_M = "measurement"


@dataclass(frozen=True)
class BoilerProfile:
    """Presentation rules for one boiler family."""

    boiler_type: str
    model: str
    # ZK value -> {"en": ..., "de": ...}
    states: dict[int, dict[str, str]]
    # ZK values during which the boiler is burning (icon only)
    firing_states: frozenset[int]
    # Störungs Nr value (as string) -> {"en": ..., "de": ...}
    error_codes: dict[str, dict[str, str]]
    standard_sensors: list[SensorSpec]
    energy_kind: str
    # Show ZK values without a name as "ZK <n>" instead of "Unknown"
    unknown_state_as_number: bool = False
    notes: dict[str, str] = field(default_factory=dict)

    def state_name(self, zk: int, language: str) -> str:
        """Return the display name for a ZK value.

        Values without a name show as "ZK <n>" when unknown_state_as_number is
        set (so new states can be spotted and named), otherwise as "Unknown".
        """
        lang = language.lower()
        entry = self.states.get(zk)
        if entry:
            return entry.get(lang, entry["en"])
        if self.unknown_state_as_number:
            return f"ZK {zk}"
        return "Unbekannt" if lang == "de" else "Unknown"

    def state_options(self, language: str) -> list[str]:
        """All known state names, for the ENUM sensor's option list."""
        lang = language.lower()
        return [v.get(lang, v["en"]) for _, v in sorted(self.states.items())]

    def error_name(self, code: str, language: str) -> str | None:
        """Return the fault text for a Störungs Nr value, or None if unknown."""
        entry = self.error_codes.get(code)
        if entry:
            return entry.get(language.lower(), entry["en"])
        return None


# =============================================================================
# Pellet boilers (Nano-PK, Classic, HSV, ...) - behaviour exactly as before
# =============================================================================
PELLET_STANDARD_SENSORS: list[SensorSpec] = [
    # --- Kessel & Verbrennung ---
    ("TK", "Kesseltemperatur", _T, _M, "mdi:thermometer"),
    ("TKsoll", "Kessel Solltemperatur", _T, _M, "mdi:thermometer-lines"),
    ("TRG", "Rauchgastemperatur", _T, _M, "mdi:smoke"),
    ("BRT", "Brennraumtemperatur", _T, _M, "mdi:fire"),
    ("Leistung", "Ausgangsleistung", None, _M, "mdi:gauge"),
    ("Effizienz", "Wirkungsgrad", None, _M, "mdi:speedometer"),
    ("O2", "O2 Gehalt", None, _M, "mdi:chart-line"),
    ("SZist", "Saugzug Ist", None, _M, "mdi:fan"),
    # --- Puffer & Speicher ---
    ("TPo", "Puffer Oben", _T, _M, "mdi:thermometer-lines"),
    ("TPm", "Puffer Mitte", _T, _M, "mdi:thermometer-lines"),
    ("TPu", "Puffer Unten", _T, _M, "mdi:thermometer-lines"),
    ("Puff Füllgrad", "Pufferfüllgrad", None, _M, "mdi:battery-medium"),
    ("Puffer_soll oben", "Puffer Sollwert Oben", _T, _M, "mdi:thermometer-plus"),
    ("Puffer_soll unten", "Puffer Sollwert Unten", _T, _M, "mdi:thermometer-minus"),
    # --- Heizkreise ---
    ("TVL_1", "Vorlauf Heizkreis 1", _T, _M, "mdi:coolant-temperature"),
    ("TVLs_1", "Vorlauf Soll Heizkreis 1", _T, _M, "mdi:target"),
    ("TRL", "Rücklauftemperatur", _T, _M, "mdi:coolant-temperature"),
    # --- Warmwasser ---
    ("TB1", "Warmwasser", _T, _M, "mdi:water-boiler"),
    ("TBs_1", "Warmwasser Soll", _T, _M, "mdi:target"),
    # --- Außentemperatur ---
    ("Taus", "Außentemperatur", _T, _M, "mdi:thermometer"),
    # --- Pellets ---
    ("Lagerstand", "Pelletvorrat", None, "total", "mdi:silo"),
    ("Verbrauchszähler", "Pelletverbrauch", None, "total_increasing", "mdi:counter"),
]

PELLET_PROFILE = BoilerProfile(
    boiler_type=BOILER_TYPE_PELLET,
    model="Nano-PK",
    states={
        i: {"en": en, "de": de}
        for i, (en, de) in enumerate(zip(BOILER_STATES_EN, BOILER_STATES_DE))
    },
    firing_states=frozenset({6, 7}),
    error_codes=ERROR_CODES,
    standard_sensors=PELLET_STANDARD_SENSORS,
    energy_kind=ENERGY_PELLET_CONSUMPTION,
)


# =============================================================================
# Log wood boilers (HV, Neo-HV)
# =============================================================================
# ZK states of an HV20, originally derived from three days of live DAQ logs
# (8-10 Oct 2026) and since cross-checked against a 10-file sample spanning
# JJ's whole archive (Dec 2020 - Jan 2025, firmware V10.2d1/l3/HAR.n2), and
# now also against the boiler's own "Zustand" field on web.hargassner.at
# during a live burn on 12 Oct 2026. States 4, 6, 9 and 11 are CONFIRMED
# that way; everything else is still inferred from timing, sensor values
# and fault codes. See docs/log_wood_state_uncertainty.md for the full
# evidence and open questions, including states still without a name.
#   1  fan off, O2 sensor idle                              -> off
#   13 O2 21 %, flue gas rising, "door open too long" (85)  -> door open
#   2  0-8 min, primary air ~75 %, BP1 pulses               -> start check
#   3  exactly 2 min                                        -> ignition preparation
#   4  CONFIRMED on the boiler's own display as "Zündung"
#      (ignition) - not "Anheizen"/heat-up as first guessed.
#      100 % output; ends after 10 min with fault 135
#      ("ignition not successful") if the fire does not catch -> ignition
#   6  CONFIRMED on the boiler's own display as "Leistungsbrand"
#      (full burn). 90-100 % output, flue gas up to 253 °C   -> full burn
#   7  low O2 (2.5-6.6 %), flue gas 199-238 °C; cycles with
#      6 and 8 within one burn                              -> full firing (peak output)
#   8  flue gas 127-233 °C, primary air 12-40 %; bridges
#      between 6/7 and burn-out                              -> ember preservation
#   9  CONFIRMED on the boiler's own display as "Ausbrand"
#      (burn-out). Flue gas falling; duration varies by
#      firmware era                                          -> burn-out
#   11 CONFIRMED on the boiler's own display as "Restwärme"
#      (residual heat) - not "Nachlauf"/cool-down as first guessed.
#      Fan off, 0 % output, flue gas falling; duration not
#      confirmed as a fixed 360 min (see uncertainty doc)     -> residual heat
#   12 single sample so far, seen nested inside a full-burn
#      run together with fault 24 (return-temp boost not
#      reached)                                              -> UNNAMED, likely a
#      throttled-output sub-state rather than a distinct phase
#   14 single sample so far, between "door open" and
#      "ignition preparation"                                -> UNNAMED, likely a
#      one-tick transition rather than a real state
LOG_WOOD_STATES: dict[int, dict[str, str]] = {
    0: {"en": "Unknown", "de": "Unbekannt"},
    1: {"en": "Off", "de": "Aus"},
    2: {"en": "Start check", "de": "Startprüfung"},
    3: {"en": "Ignition preparation", "de": "Zündvorbereitung"},
    4: {"en": "Ignition", "de": "Zündung"},
    6: {"en": "Full burn", "de": "Leistungsbrand"},
    7: {"en": "Full firing", "de": "Vollbrand"},
    8: {"en": "Ember preservation", "de": "Gluterhaltung"},
    9: {"en": "Burn-out", "de": "Ausbrand"},
    11: {"en": "Residual heat", "de": "Restwärme"},
    13: {"en": "Door open", "de": "Tür offen"},
}

# Fault and message numbers as listed by an HV20 (V10.2HAR.n2) under
# "Ereignisse" in the boiler's web interface. Numbers overlap with the pellet
# table but mean different things (e.g. 13, 23, 24).
LOG_WOOD_ERROR_CODES: dict[str, dict[str, str]] = {
    # 4, 6 and 16 all fired once, in the same minute, on 12 Oct 2026 - see
    # docs/log_wood_state_uncertainty.md for why that's flagged as worth a
    # physical check rather than treated as routine.
    "4": {
        "en": "Flue gas sensor wrongly connected",
        "de": "Rauchgasfühler falsch angeschlossen",
    },
    "6": {"en": "Boiler sensor short circuit", "de": "Kesselfühler Kurzschluss"},
    "13": {
        "en": "Primary air motor (A1) not working - set primary air flap to 20 % by hand",
        "de": "Primärmotor (A1) arbeitet nicht. Primärluftklappe per Hand auf 20% stellen.",
    },
    "16": {
        "en": "Return sensor short circuit",
        "de": "Rücklauffühler Kurzschluss",
    },
    "23": {
        "en": "Clean the log wood boiler's heating surfaces",
        "de": "Stückholzkessel Heizflächen reinigen",
    },
    "24": {
        "en": "Return temperature boost not reached",
        "de": "Rücklaufanhebung Temperatur nicht erreicht",
    },
    "85": {"en": "Boiler door open too long", "de": "Kesseltür zu lange offen"},
    "88": {
        "en": "External heat sensor disconnected",
        "de": "Fremdwärmefühler Unterbrechung",
    },
    "90": {"en": "Boiler I/O not connected", "de": "Kessel-IO nicht angeschlossen"},
    "99": {"en": "Boiler overtemperature", "de": "Kessel Übertemperatur!"},
    "135": {"en": "Ignition not successful", "de": "Zündung nicht erfolgreich"},
    "305": {
        "en": "Maximum flue gas temperature exceeded",
        "de": "Maximale Rauchgastemperatur überschritten",
    },
    "309": {"en": "Add wood", "de": "Nachlegen"},
    "310": {
        "en": "Boiler temperature exceeded 92 °C during last burn",
        "de": "Achtung: Kesseltemperatur bei letztem Abbrand erreichte über 92°C",
    },
    "380": {
        "en": "Maintenance due - have factory service carried out",
        "de": "Wartung fällig! Werkswartung durchführen lassen!",
    },
    "460": {"en": "Clean boiler", "de": "Kessel reinigen"},
    "7101": {
        "en": "Max. hot water charging time exceeded - check sensor position and flow, contact installer",
        "de": "max. Boilerladezeit überschritten, Boilerladung träge! Fühlerposition prüfen, "
        "Durchfluss prüfen, Heizungsbauer kontaktieren",
    },
}

LOG_WOOD_STANDARD_SENSORS: list[SensorSpec] = [
    # --- Kessel & Verbrennung ---
    ("TK", "Kesseltemperatur", _T, _M, "mdi:thermometer"),
    ("TKsoll", "Kessel Solltemperatur", _T, _M, "mdi:thermometer-lines"),
    ("TRG", "Rauchgastemperatur", _T, _M, "mdi:smoke"),
    ("Leistung", "Ausgangsleistung", None, _M, "mdi:gauge"),
    ("O2", "O2 Gehalt", None, _M, "mdi:chart-line"),
    ("SZist", "Saugzug Ist", None, _M, "mdi:fan"),
    ("Prim.ist", "Primärluft Ist", None, _M, "mdi:air-filter"),
    ("Sek.ist", "Sekundärluft Ist", None, _M, "mdi:air-filter"),
    ("TRL", "Rücklauftemperatur", _T, _M, "mdi:coolant-temperature"),
    ("TRLsoll", "Rücklauf Solltemperatur", _T, _M, "mdi:target"),
    # --- Puffer ---
    ("TPo", "Puffer Oben", _T, _M, "mdi:thermometer-lines"),
    ("TPm", "Puffer Mitte", _T, _M, "mdi:thermometer-lines"),
    ("TPu", "Puffer Unten", _T, _M, "mdi:thermometer-lines"),
    ("PufLad", "Pufferfüllgrad", None, _M, "mdi:battery-medium"),
    ("PufZustand", "Pufferzustand", None, None, "mdi:state-machine"),
    ("Spreizung", "Temperaturspreizung", _T, _M, "mdi:arrow-expand-vertical"),
    ("RLP/PuffPumpe", "Pufferpumpe", None, _M, "mdi:pump"),
    ("Puffer_soll oben", "Puffer Sollwert Oben", _T, _M, "mdi:thermometer-plus"),
    ("Puffer_soll unten", "Puffer Sollwert Unten", _T, _M, "mdi:thermometer-minus"),
    ("Max Anf ZenPuf", "Höchste Anforderung", _T, _M, "mdi:thermometer-alert"),
    # --- Warmwasser ---
    ("TB1", "Warmwasser", _T, _M, "mdi:water-boiler"),
    ("TBs_1", "Warmwasser Soll", _T, _M, "mdi:target"),
    ("BoiZustand_1", "Boilerzustand 1", None, None, "mdi:state-machine"),
    ("BP1", "Boilerpumpe 1", None, None, "mdi:pump"),
    # --- Steuerung ---
    ("Tplat", "Platinentemperatur", _T, _M, "mdi:chip"),
]

LOG_WOOD_PROFILE = BoilerProfile(
    boiler_type=BOILER_TYPE_LOG_WOOD,
    model="HV",
    states=LOG_WOOD_STATES,
    firing_states=frozenset({4, 6, 7, 8, 9}),
    error_codes=LOG_WOOD_ERROR_CODES,
    standard_sensors=LOG_WOOD_STANDARD_SENSORS,
    energy_kind=ENERGY_BUFFER_STORED,
    unknown_state_as_number=True,
    notes={
        "states": "unconfirmed - inferred from HV20 DAQ logs across the full "
        "archive; see docs/log_wood_state_uncertainty.md"
    },
)


PROFILES: Final[dict[str, BoilerProfile]] = {
    BOILER_TYPE_PELLET: PELLET_PROFILE,
    BOILER_TYPE_LOG_WOOD: LOG_WOOD_PROFILE,
}


def get_profile(boiler_type: str | None) -> BoilerProfile:
    """Return the profile for a boiler type; anything unknown is treated as pellet."""
    return PROFILES.get(boiler_type or BOILER_TYPE_PELLET, PELLET_PROFILE)


def buffer_stored_energy_kwh(
    temperatures: list[float], volume_l: float, reference_c: float
) -> float:
    """Heat stored in the buffer above a reference temperature, in kWh.

    Treats each sensor as representing an equal slice of the tank. Water holds
    1.163 Wh per litre per kelvin. Never negative: a buffer below the reference
    holds no usable heat.
    """
    if not temperatures:
        raise ValueError("no buffer temperatures")
    mean = sum(temperatures) / len(temperatures)
    return max(0.0, volume_l * 1.163 * (mean - reference_c) / 1000.0)
