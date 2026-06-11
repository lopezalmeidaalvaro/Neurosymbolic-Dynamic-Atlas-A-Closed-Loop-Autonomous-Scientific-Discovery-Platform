#!/usr/bin/env python3
"""
test_space_protocol_stack.py
=============================
V&V Test Suite — Space Communications Protocol Stack
Authority  : Verification & Validation Lead (ESA/NASA Standard)
Document ID: AST-TEST-COMMS-001
Target     : satellite/comms/space_protocol_stack.py  (Lines 12-178)
CDR Gate   : AI-CDR-02  (Coverage >= 80%)

Coverage targets:
  - CCSDSProtocol.pack_ccsds_packet
  - CCSDSProtocol.unpack_ccsds_packet
  - SpaceWireProtocol.calculate_crc8
  - SpaceWireProtocol.create_spw_packet
  - SpaceWireProtocol.parse_spw_packet
  - CANAerospaceProtocol.pack_can_thermal_telemetry
  - CANAerospaceProtocol.unpack_can_frame
  - CubeSatSpaceProtocol.create_csp_command
  - CubeSatSpaceProtocol.parse_csp_response
"""

import os
import sys
import struct
import math
import pytest

# ---------------------------------------------------------------------------
# Module under test
# ---------------------------------------------------------------------------
COMMS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "satellite", "comms"
)
sys.path.insert(0, COMMS_DIR)

from space_protocol_stack import (
    CCSDSProtocol,
    SpaceWireProtocol,
    CANAerospaceProtocol,
    CubeSatSpaceProtocol,
)

# ===========================================================================
# 1. CCSDSProtocol
# ===========================================================================


class TestCCSDSProtocol:
    """CCSDS 133.0-B-1 Space Packet Protocol — pack/unpack round-trip."""

    SAMPLE_PAYLOAD = b"\x01\x02\x03\x04"

    def test_pack_returns_bytes(self):
        result = CCSDSProtocol.pack_ccsds_packet(100, 0, self.SAMPLE_PAYLOAD)
        assert isinstance(result, bytes)

    def test_packed_length_is_6_plus_payload(self):
        result = CCSDSProtocol.pack_ccsds_packet(100, 0, self.SAMPLE_PAYLOAD)
        assert len(result) == 6 + len(self.SAMPLE_PAYLOAD)

    def test_unpack_recovers_apid(self):
        apid = 0x1A3
        raw = CCSDSProtocol.pack_ccsds_packet(apid, 0, self.SAMPLE_PAYLOAD)
        parsed = CCSDSProtocol.unpack_ccsds_packet(raw)
        assert parsed["apid"] == apid

    def test_unpack_recovers_sequence_count(self):
        seq = 42
        raw = CCSDSProtocol.pack_ccsds_packet(100, seq, self.SAMPLE_PAYLOAD)
        parsed = CCSDSProtocol.unpack_ccsds_packet(raw)
        assert parsed["seq_count"] == seq

    def test_unpack_recovers_payload(self):
        raw = CCSDSProtocol.pack_ccsds_packet(100, 0, self.SAMPLE_PAYLOAD)
        parsed = CCSDSProtocol.unpack_ccsds_packet(raw)
        assert parsed["payload"] == self.SAMPLE_PAYLOAD

    def test_unpack_seq_flags_are_unsegmented(self):
        """Sequence flags should be 3 (unsegmented)."""
        raw = CCSDSProtocol.pack_ccsds_packet(100, 0, self.SAMPLE_PAYLOAD)
        parsed = CCSDSProtocol.unpack_ccsds_packet(raw)
        assert parsed["seq_flags"] == 3

    def test_unpack_version_is_zero(self):
        raw = CCSDSProtocol.pack_ccsds_packet(100, 0, self.SAMPLE_PAYLOAD)
        parsed = CCSDSProtocol.unpack_ccsds_packet(raw)
        assert parsed["version"] == 0

    def test_unpack_type_is_telemetry(self):
        raw = CCSDSProtocol.pack_ccsds_packet(100, 0, self.SAMPLE_PAYLOAD)
        parsed = CCSDSProtocol.unpack_ccsds_packet(raw)
        assert parsed["type"] == 0  # TM (telemetry) = 0

    def test_unpack_raises_for_short_buffer(self):
        with pytest.raises(ValueError, match="too short"):
            CCSDSProtocol.unpack_ccsds_packet(b"\x00\x01\x02")

    def test_apid_masked_to_11_bits(self):
        """APID is 11 bits wide — mask should be applied."""
        raw = CCSDSProtocol.pack_ccsds_packet(0xFFFF, 0, b"\xaa\xbb")
        parsed = CCSDSProtocol.unpack_ccsds_packet(raw)
        assert parsed["apid"] == 0x07FF  # 11-bit mask

    def test_sequence_count_masked_to_14_bits(self):
        """Sequence count is 14 bits wide."""
        raw = CCSDSProtocol.pack_ccsds_packet(100, 0xFFFF, b"\xaa")
        parsed = CCSDSProtocol.unpack_ccsds_packet(raw)
        assert parsed["seq_count"] == 0x3FFF

    def test_max_apid_zero(self):
        """APID=0 is valid (management/housekeeping)."""
        raw = CCSDSProtocol.pack_ccsds_packet(0, 0, b"\x00")
        parsed = CCSDSProtocol.unpack_ccsds_packet(raw)
        assert parsed["apid"] == 0

    def test_round_trip_large_payload(self):
        payload = bytes(range(128))
        raw = CCSDSProtocol.pack_ccsds_packet(200, 100, payload)
        parsed = CCSDSProtocol.unpack_ccsds_packet(raw)
        assert parsed["payload"] == payload


# ===========================================================================
# 2. SpaceWireProtocol
# ===========================================================================


class TestSpaceWireProtocol:
    """ECSS-E-ST-50-12C SpaceWire packet — CRC-8, pack/unpack."""

    def test_calculate_crc8_returns_int(self):
        result = SpaceWireProtocol.calculate_crc8(b"\x01\x02\x03")
        assert isinstance(result, int)
        assert 0 <= result <= 255

    def test_crc8_empty_data_is_zero(self):
        """CRC-8 of empty byte string starting at 0x00 = 0."""
        result = SpaceWireProtocol.calculate_crc8(b"")
        assert result == 0

    def test_crc8_deterministic(self):
        data = b"\xde\xad\xbe\xef"
        assert SpaceWireProtocol.calculate_crc8(
            data
        ) == SpaceWireProtocol.calculate_crc8(data)

    def test_crc8_changes_with_data(self):
        assert SpaceWireProtocol.calculate_crc8(
            b"\x00"
        ) != SpaceWireProtocol.calculate_crc8(b"\x01")

    def test_create_packet_returns_bytes(self):
        pkt = SpaceWireProtocol.create_spw_packet(0xFE, 0x01, b"\xab\xcd")
        assert isinstance(pkt, bytes)

    def test_packet_length_is_header_plus_payload_plus_crc(self):
        payload = b"\x10\x20\x30"
        pkt = SpaceWireProtocol.create_spw_packet(0xFE, 0x02, payload)
        # 1 (log_addr) + 1 (proto_id) + len(payload) + 1 (CRC) = 6
        assert len(pkt) == 2 + len(payload) + 1

    def test_parse_recovers_logical_address(self):
        pkt = SpaceWireProtocol.create_spw_packet(0xFE, 0x01, b"\xaa")
        parsed = SpaceWireProtocol.parse_spw_packet(pkt)
        assert parsed["logical_address"] == 0xFE

    def test_parse_recovers_protocol_id(self):
        pkt = SpaceWireProtocol.create_spw_packet(0xFE, 0x05, b"\xaa")
        parsed = SpaceWireProtocol.parse_spw_packet(pkt)
        assert parsed["protocol_id"] == 0x05

    def test_parse_recovers_payload(self):
        payload = b"\x11\x22\x33"
        pkt = SpaceWireProtocol.create_spw_packet(0xFE, 0x01, payload)
        parsed = SpaceWireProtocol.parse_spw_packet(pkt)
        assert parsed["payload"] == payload

    def test_crc_ok_for_valid_packet(self):
        pkt = SpaceWireProtocol.create_spw_packet(0xFE, 0x01, b"\xab\xcd\xef")
        parsed = SpaceWireProtocol.parse_spw_packet(pkt)
        assert parsed["crc_ok"] is True

    def test_crc_fails_for_corrupted_packet(self):
        pkt = bytearray(SpaceWireProtocol.create_spw_packet(0xFE, 0x01, b"\x01\x02"))
        pkt[-1] ^= 0xFF  # Corrupt the CRC byte
        parsed = SpaceWireProtocol.parse_spw_packet(bytes(pkt))
        assert parsed["crc_ok"] is False

    def test_parse_raises_for_short_buffer(self):
        with pytest.raises(ValueError, match="too short"):
            SpaceWireProtocol.parse_spw_packet(b"\x01\x02")

    def test_round_trip_empty_payload(self):
        pkt = SpaceWireProtocol.create_spw_packet(0x01, 0x00, b"")
        parsed = SpaceWireProtocol.parse_spw_packet(pkt)
        assert parsed["payload"] == b""
        assert parsed["crc_ok"] is True


# ===========================================================================
# 3. CANAerospaceProtocol
# ===========================================================================


class TestCANAerospaceProtocol:
    """CAN Aerospace 2.0B thermal telemetry frame — pack/unpack."""

    def test_pack_returns_tuple(self):
        result = CANAerospaceProtocol.pack_can_thermal_telemetry(0, 25.0, 15.0)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_can_id_is_0x700_plus_node(self):
        can_id, _ = CANAerospaceProtocol.pack_can_thermal_telemetry(3, 25.0, 15.0)
        assert can_id == 0x703

    def test_can_id_node_masked_to_4_bits(self):
        can_id, _ = CANAerospaceProtocol.pack_can_thermal_telemetry(0x1F, 25.0, 15.0)
        assert can_id == 0x700 + (0x1F & 0x0F)

    def test_payload_is_8_bytes(self):
        _, payload = CANAerospaceProtocol.pack_can_thermal_telemetry(0, 25.0, 15.0)
        assert len(payload) == 8

    def test_unpack_recovers_temperature(self):
        can_id, payload = CANAerospaceProtocol.pack_can_thermal_telemetry(0, 37.5, 10.0)
        parsed = CANAerospaceProtocol.unpack_can_frame(can_id, payload)
        assert math.isclose(parsed["temperature"], 37.5, rel_tol=1e-5)

    def test_unpack_recovers_power(self):
        can_id, payload = CANAerospaceProtocol.pack_can_thermal_telemetry(0, 37.5, 10.0)
        parsed = CANAerospaceProtocol.unpack_can_frame(can_id, payload)
        assert math.isclose(parsed["power_w"], 10.0, rel_tol=1e-5)

    def test_unpack_recovers_node_id(self):
        can_id, payload = CANAerospaceProtocol.pack_can_thermal_telemetry(4, 25.0, 5.0)
        parsed = CANAerospaceProtocol.unpack_can_frame(can_id, payload)
        assert parsed["node_id"] == 4

    def test_unpack_raises_for_short_payload(self):
        with pytest.raises(ValueError, match="too short"):
            CANAerospaceProtocol.unpack_can_frame(0x700, b"\x01\x02\x03")

    def test_negative_temperature(self):
        can_id, payload = CANAerospaceProtocol.pack_can_thermal_telemetry(1, -40.0, 3.0)
        parsed = CANAerospaceProtocol.unpack_can_frame(can_id, payload)
        assert math.isclose(parsed["temperature"], -40.0, rel_tol=1e-5)

    def test_all_six_nodes(self):
        for node_id in range(6):
            can_id, payload = CANAerospaceProtocol.pack_can_thermal_telemetry(
                node_id, 20.0 + node_id, 5.0
            )
            parsed = CANAerospaceProtocol.unpack_can_frame(can_id, payload)
            assert parsed["node_id"] == node_id


# ===========================================================================
# 4. CubeSatSpaceProtocol
# ===========================================================================


class TestCubeSatSpaceProtocol:
    """CSP commands and responses on Port 15 (Active Thermal Service)."""

    def test_create_command_returns_bytes(self):
        result = CubeSatSpaceProtocol.create_csp_command(0x01, 27.5)
        assert isinstance(result, bytes)

    def test_command_length_is_6_bytes(self):
        """2 (header) + 4 (float) = 6 bytes."""
        result = CubeSatSpaceProtocol.create_csp_command(0x01, 27.5)
        assert len(result) == 6

    def test_parse_csp_response_returns_dict(self):
        raw = CubeSatSpaceProtocol.create_csp_command(0x01, 30.0)
        parsed = CubeSatSpaceProtocol.parse_csp_response(raw)
        assert isinstance(parsed, dict)

    def test_parse_recovers_value(self):
        raw = CubeSatSpaceProtocol.create_csp_command(0x02, 42.0)
        parsed = CubeSatSpaceProtocol.parse_csp_response(raw)
        assert math.isclose(parsed["value"], 42.0, rel_tol=1e-5)

    def test_parse_recovers_command_code(self):
        raw = CubeSatSpaceProtocol.create_csp_command(0x02, 0.0)
        parsed = CubeSatSpaceProtocol.parse_csp_response(raw)
        assert parsed["command_code"] == 0x02

    def test_command_name_predict(self):
        raw = CubeSatSpaceProtocol.create_csp_command(0x01, 0.0)
        parsed = CubeSatSpaceProtocol.parse_csp_response(raw)
        assert parsed["command_name"] == "CSP_THERMAL_PREDICT"

    def test_command_name_status(self):
        raw = CubeSatSpaceProtocol.create_csp_command(0x02, 0.0)
        parsed = CubeSatSpaceProtocol.parse_csp_response(raw)
        assert parsed["command_name"] == "CSP_THERMAL_STATUS"

    def test_command_name_throttle(self):
        raw = CubeSatSpaceProtocol.create_csp_command(0x03, 0.5)
        parsed = CubeSatSpaceProtocol.parse_csp_response(raw)
        assert parsed["command_name"] == "CSP_THROTTLE"

    def test_unknown_command_code_returns_csp_unknown(self):
        raw = CubeSatSpaceProtocol.create_csp_command(0x3F, 0.0)
        parsed = CubeSatSpaceProtocol.parse_csp_response(raw)
        assert parsed["command_name"] == "CSP_UNKNOWN"

    def test_src_port_is_15(self):
        raw = CubeSatSpaceProtocol.create_csp_command(0x01, 0.0)
        parsed = CubeSatSpaceProtocol.parse_csp_response(raw)
        assert parsed["src_port"] == 15

    def test_dest_port_is_15(self):
        raw = CubeSatSpaceProtocol.create_csp_command(0x01, 0.0)
        parsed = CubeSatSpaceProtocol.parse_csp_response(raw)
        assert parsed["dest_port"] == 15

    def test_parse_raises_for_short_response(self):
        with pytest.raises(ValueError, match="too short"):
            CubeSatSpaceProtocol.parse_csp_response(b"\x00\x01\x02")

    def test_negative_float_value(self):
        raw = CubeSatSpaceProtocol.create_csp_command(0x03, -273.15)
        parsed = CubeSatSpaceProtocol.parse_csp_response(raw)
        assert math.isclose(parsed["value"], -273.15, rel_tol=1e-4)

    def test_command_code_masked_to_6_bits(self):
        """Command code is 6 bits — values > 63 must be masked."""
        raw = CubeSatSpaceProtocol.create_csp_command(0xFF, 0.0)
        parsed = CubeSatSpaceProtocol.parse_csp_response(raw)
        assert parsed["command_code"] == 0xFF & 0x3F
