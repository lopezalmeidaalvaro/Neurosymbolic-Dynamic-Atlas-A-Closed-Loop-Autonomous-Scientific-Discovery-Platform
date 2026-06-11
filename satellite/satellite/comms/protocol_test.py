#!/usr/bin/env python3
"""
Autonomous Spacecraft Thermal OS - Space Protocols Test Harness
==============================================================
Performs unit tests for CCSDS Space Packet, SpaceWire, CAN Aerospace,
and CubeSat Space Protocol (CSP) codecs.
"""

import sys
from space_protocol_stack import (
    CCSDSProtocol,
    SpaceWireProtocol,
    CANAerospaceProtocol,
    CubeSatSpaceProtocol,
)


def test_ccsds_codec():
    print("Testing CCSDS 133.0-B-1 Packet Protocol...")
    payload = b"\x01\x02\x03\x04\x42"
    apid = 0x14
    seq = 412

    packed = CCSDSProtocol.pack_ccsds_packet(apid, seq, payload)
    unpacked = CCSDSProtocol.unpack_ccsds_packet(packed)

    assert unpacked["apid"] == apid, "CCSDS APID mismatch"
    assert unpacked["seq_count"] == seq, "CCSDS Sequence Count mismatch"
    assert unpacked["payload"] == payload, "CCSDS Payload mismatch"
    print("  [PASS] CCSDS packet pack/unpack successful.")


def test_spacewire_codec():
    print("Testing SpaceWire ECSS-E-ST-50-12C...")
    logical_address = 0xFE
    protocol_id = 0x06
    payload = b"ThermalTwinTelemetryData"

    packed = SpaceWireProtocol.create_spw_packet(logical_address, protocol_id, payload)
    parsed = SpaceWireProtocol.parse_spw_packet(packed)

    assert (
        parsed["logical_address"] == logical_address
    ), "SpaceWire logical address mismatch"
    assert parsed["protocol_id"] == protocol_id, "SpaceWire Protocol ID mismatch"
    assert parsed["payload"] == payload, "SpaceWire payload mismatch"
    assert parsed["crc_ok"] == True, "SpaceWire CRC mismatch"
    print("  [PASS] SpaceWire packet routing and CRC-8 successful.")


def test_can_aerospace_codec():
    print("Testing CAN Aerospace 2.0B...")
    node_id = 4  # CPU Node
    temp = 42.15
    power = 18.0

    can_id, payload = CANAerospaceProtocol.pack_can_thermal_telemetry(
        node_id, temp, power
    )
    unpacked = CANAerospaceProtocol.unpack_can_frame(can_id, payload)

    assert unpacked["node_id"] == node_id, "CAN Node ID mismatch"
    assert abs(unpacked["temperature"] - temp) < 1e-4, "CAN Temperature mismatch"
    assert abs(unpacked["power_w"] - power) < 1e-4, "CAN Power mismatch"
    print("  [PASS] CAN 29-bit identifier and thermal telemetry packing successful.")


def test_csp_codec():
    print("Testing CubeSat Space Protocol (CSP) active commands...")
    cmd_code = 3  # CSP_THROTTLE
    value = 0.40  # 40% CPU limit

    packed = CubeSatSpaceProtocol.create_csp_command(cmd_code, value)
    parsed = CubeSatSpaceProtocol.parse_csp_response(packed)

    assert parsed["command_code"] == cmd_code, "CSP Command Code mismatch"
    assert parsed["command_name"] == "CSP_THROTTLE", "CSP Command Name mapping mismatch"
    assert abs(parsed["value"] - value) < 1e-4, "CSP Command Value mismatch"
    print("  [PASS] CSP active thermal service commands successful.")


if __name__ == "__main__":
    print("==============================================================")
    print("RUNNING AEROSPACE PROTOCOLS TEST HARNESS...")
    print("==============================================================")
    try:
        test_ccsds_codec()
        test_spacewire_codec()
        test_can_aerospace_codec()
        test_csp_codec()
        print("==============================================================")
        print("ALL SPACE COMMUNICATION PROTOCOLS TESTS PASSED successfully!")
        print("==============================================================")
    except AssertionError as ex:
        print(f"  [FAIL] Assertion failed: {str(ex)}")
        sys.exit(1)
