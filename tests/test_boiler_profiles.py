"""Boiler profiles: pellet behaviour unchanged, log wood profile consistent."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from conftest import FIRMWARE_TEMPLATES, load_module

const = load_module("const")
profiles = load_module("boiler_profiles")


def channel_units(firmware: str) -> dict[str, str | None]:
    """Name -> unit for every channel (analog and digital) in a template."""
    root = ET.fromstring(FIRMWARE_TEMPLATES[firmware])
    return {ch.get("name"): ch.get("unit") for ch in root.iter("CHANNEL")}


# --- firmware <-> boiler type -------------------------------------------------


def test_every_firmware_has_a_boiler_type():
    """Each offered firmware belongs to exactly one type's list."""
    by_type = [fw for t in const.BOILER_TYPES for fw in const.firmware_versions_for(t)]
    assert sorted(by_type) == sorted(const.FIRMWARE_VERSIONS)


def test_hv20_is_log_wood_and_pellet_templates_stay_pellet():
    hv20_firmwares = {"V10_2HAR_n2", "V10_2HAR_p"}
    for fw in hv20_firmwares:
        assert const.boiler_type_for_firmware(fw) == const.BOILER_TYPE_LOG_WOOD
    for fw in const.FIRMWARE_VERSIONS:
        if fw not in hv20_firmwares:
            assert const.boiler_type_for_firmware(fw) == const.BOILER_TYPE_PELLET


def test_unknown_or_missing_type_falls_back_to_pellet():
    assert profiles.get_profile(None) is profiles.PELLET_PROFILE
    assert profiles.get_profile("something") is profiles.PELLET_PROFILE
    assert const.boiler_type_for_firmware(None) == const.BOILER_TYPE_PELLET


# --- pellet profile: identical to the pre-profile behaviour -------------------


def test_pellet_states_match_the_old_lists():
    p = profiles.PELLET_PROFILE
    assert p.state_options("en") == list(const.BOILER_STATES_EN)
    assert p.state_options("de") == list(const.BOILER_STATES_DE)
    assert p.state_name(7, "en") == "Full firing"
    assert p.state_name(99, "en") == "Unknown"
    assert p.state_name(99, "de") == "Unbekannt"


def test_pellet_errors_are_the_old_table():
    assert profiles.PELLET_PROFILE.error_codes is const.ERROR_CODES
    assert profiles.PELLET_PROFILE.firing_states == {6, 7}
    assert profiles.PELLET_PROFILE.model == "Nano-PK"


def test_pellet_standard_set_is_unchanged():
    keys = [spec[0] for spec in profiles.PELLET_PROFILE.standard_sensors]
    assert len(keys) == 22
    assert {"BRT", "Effizienz", "Puff Füllgrad", "Lagerstand", "Verbrauchszähler"} <= set(keys)


# --- log wood profile ---------------------------------------------------------


@pytest.mark.parametrize("firmware", const.LOG_WOOD_FIRMWARE_VERSIONS)
def test_log_wood_standard_sensors_exist_in_template(firmware):
    """No STANDARD sensor for log wood stays permanently unknown."""
    units = channel_units(firmware)
    missing = [s[0] for s in profiles.LOG_WOOD_PROFILE.standard_sensors if s[0] not in units]
    assert missing == []


@pytest.mark.parametrize("firmware", const.LOG_WOOD_FIRMWARE_VERSIONS)
def test_log_wood_temperature_sensors_are_celsius(firmware):
    """Home Assistant rejects a temperature device class without a temperature unit."""
    units = channel_units(firmware)
    wrong = [
        s[0]
        for s in profiles.LOG_WOOD_PROFILE.standard_sensors
        if s[2] == "temperature" and units.get(s[0]) != "°C"
    ]
    assert wrong == []


def test_log_wood_states():
    p = profiles.LOG_WOOD_PROFILE
    assert p.state_name(1, "de") == "Aus"
    assert p.state_name(6, "en") == "Full burn"
    assert p.state_name(7, "en") == "Full firing"
    assert p.state_name(8, "de") == "Gluterhaltung"
    assert p.state_name(11, "de") == "Restwärme"
    assert p.state_name(13, "en") == "Door open"
    # Unnamed values keep their number so they can be identified later.
    # 5 has never been observed; 12 and 14 have been seen in the DAQ
    # archive but only once each, so they stay unnamed until confirmed.
    assert p.state_name(5, "en") == "ZK 5"
    assert p.state_name(12, "en") == "ZK 12"
    assert p.state_name(14, "en") == "ZK 14"
    assert p.firing_states == {4, 6, 7, 8, 9}
    assert p.model == "HV"


def test_log_wood_errors_differ_from_pellet_where_numbers_overlap():
    wood = profiles.LOG_WOOD_PROFILE
    assert wood.error_name("135", "de") == "Zündung nicht erfolgreich"
    assert wood.error_name("309", "en") == "Add wood"
    assert wood.error_name("13", "en") != const.ERROR_CODES["13"]["en"]
    assert wood.error_name("1", "en") is None  # not an HV20 code


@pytest.mark.parametrize("profile", list(profiles.PROFILES.values()))
def test_texts_have_both_languages(profile):
    for table in (profile.states, profile.error_codes):
        for entry in table.values():
            assert entry["en"] and entry["de"]


@pytest.mark.parametrize("profile", list(profiles.PROFILES.values()))
def test_sensor_classes_are_valid_home_assistant_values(profile):
    device_classes = {None, "temperature"}
    state_classes = {None, "measurement", "total", "total_increasing"}
    for key, _name, device_class, state_class, _icon in profile.standard_sensors:
        assert device_class in device_classes, key
        assert state_class in state_classes, key


# --- buffer energy ------------------------------------------------------------


def test_buffer_energy_matches_hand_calculation():
    # 1600 l at a mean of 34.33 °C, 30 °C reference: 1600 * 1.163 * 4.33 / 1000
    kwh = profiles.buffer_stored_energy_kwh([35, 34, 34], 1600, 30)
    assert kwh == pytest.approx(1600 * 1.163 * (103 / 3 - 30) / 1000)
    assert kwh == pytest.approx(8.06, abs=0.01)


def test_buffer_energy_full_buffer():
    # 9 Oct 2026 03:00 from the DAQ log: 72.1 / 71.3 / 56.5 °C
    assert profiles.buffer_stored_energy_kwh([72.1, 71.3, 56.5], 1600, 30) == pytest.approx(
        68.2, abs=0.1
    )


def test_buffer_energy_never_negative():
    assert profiles.buffer_stored_energy_kwh([20.9, 20.9, 20.4], 1600, 30) == 0.0


def test_buffer_energy_needs_temperatures():
    with pytest.raises(ValueError):
        profiles.buffer_stored_energy_kwh([], 1600, 30)
