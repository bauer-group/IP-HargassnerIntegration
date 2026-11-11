"""DAQ file decompression (HISDAQ TOKEN-ESC)."""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import REPO_ROOT

import daq_parser  # tools/ is on sys.path via conftest


def token(distance: int, length: int) -> bytes:
    """Encode a back-reference token: 0x10-0x13 lead byte, 26-bit value."""
    v = (distance << 13) | length
    return bytes([0x10 | ((v >> 24) & 0x03), (v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF])


def test_literals_pass_through():
    assert daq_parser.decompress_token_esc(b"pm 1 2 3\r\n") == b"pm 1 2 3\r\n"


def test_back_reference_copies_earlier_output():
    data = b"pm 1 2 3\r\n" + token(10, 10)
    assert daq_parser.decompress_token_esc(data) == b"pm 1 2 3\r\n" * 2


def test_overlapping_copy_repeats_pattern():
    # distance 3, length 6 over "abc" -> "abcabc" appended
    assert daq_parser.decompress_token_esc(b"abc" + token(3, 6)) == b"abcabcabc"


def test_large_values_use_low_bits_of_lead_byte():
    # distance is 13 bits (max 8191); the top 2 bits of the 26-bit value sit in
    # the lead byte, so distance >= 2048 makes the lead byte 0x11-0x13
    literal = bytes(range(32, 127)) * 100  # 9500 bytes
    tok = token(8000, 5)
    assert tok[0] != 0x10
    out = daq_parser.decompress_token_esc(literal + tok)
    assert out == literal + literal[1500:1505]


def test_uncompressed_file_is_returned_unchanged():
    raw = b"<HISDAQ-V0.1>\r\n<DAQPRJ></DAQPRJ>\r\npm 1 2\r\n"
    assert daq_parser.read_daq_bytes(raw) == raw


def test_compressed_file_header_kept_and_data_expanded():
    header = b"<HISDAQ-V0.1;COMPRESSION(TOKEN-ESC(4B, 0x10, 6, 13, 13))>\r\n<DAQPRJ></DAQPRJ>"
    line = b"\r\n2026-10-08_00:00:00 pm 1 0.4 0\r\n"
    out = daq_parser.read_daq_bytes(header + line + token(len(line) - 2, len(line) - 2))
    assert out == header + line + line[2:]


def test_parser_finds_timestamped_samples(tmp_path: Path):
    header = b"<HISDAQ-V0.1;COMPRESSION(TOKEN-ESC(4B, 0x10, 6, 13, 13))>\r\n"
    prj = (
        b"<DAQPRJ><ANALOG><CHANNEL id='0' name='ZK' dop='0'/>"
        b"<CHANNEL id='1' name='TK' unit='\xb0C'/></ANALOG><DIGITAL></DIGITAL></DAQPRJ>"
    )
    line = b"\r\n2026-10-08_00:00:01 pm 1 20.5"
    path = tmp_path / "TEST.DAQ"
    path.write_bytes(header + prj + line + token(len(line), len(line)) + b"\r\n")

    data = daq_parser.DAQParser(str(path)).parse()

    assert data.sample_messages == ["pm 1 20.5", "pm 1 20.5"]
    assert [p.name for p in data.analog_parameters] == ["ZK", "TK"]


@pytest.mark.parametrize(
    "path",
    sorted((REPO_ROOT / "tools" / "DAQ files").glob("*.DAQ")),
    ids=lambda p: p.name,
)
def test_real_hv20_files_decode_to_whole_lines(path: Path):
    """Only runs where real DAQ files are present locally."""
    data = daq_parser.DAQParser(str(path)).parse()
    lengths = {len(m.split()) - 1 for m in data.sample_messages}
    assert data.sample_messages, "no pm lines decoded"
    assert len(lengths) == 1, f"inconsistent value counts {lengths}"
