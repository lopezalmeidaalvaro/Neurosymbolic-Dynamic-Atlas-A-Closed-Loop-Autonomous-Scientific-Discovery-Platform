#!/usr/bin/env python3
"""
Autonomous Spacecraft Thermal OS - Space Communications Protocol Stack
======================================================================
Implements standard flight protocol framing layers: CCSDS Space Packet,
SpaceWire (ECSS-E-ST-50-12C), CAN Aerospace 2.0B, and CubeSat Space Protocol (CSP).
"""

import struct


class CCSDSProtocol:
    """
    CCSDS 133.0-B-1 Space Packet Protocol implementation.
    Primary Header: 6 bytes
    - Version (3 bits) | Type (1 bit) | Secondary Header Flag (1 bit) | APID (11 bits)
    - Sequence Flags (2 bits) | Sequence Count (14 bits)
    - Packet Data Length (16 bits) -> Data size minus 1
    """

    @staticmethod
    def pack_ccsds_packet(apid: int, sequence_count: int, payload: bytes) -> bytes:
        # Version 0, Type 0 (telemetry), SecHdr 0
        p_id = (0 << 13) | (0 << 12) | (0 << 11) | (apid & 0x07FF)
        # Sequence flags: 3 (unsegmented data)
        p_seq = (3 << 14) | (sequence_count & 0x3FFF)
        length = len(payload) - 1

        header = struct.pack(">HHH", p_id, p_seq, length)
        return header + payload

    @staticmethod
    def unpack_ccsds_packet(raw_bytes: bytes) -> dict:
        if len(raw_bytes) < 6:
            raise ValueError("Buffer too short for CCSDS primary header.")

        p_id, p_seq, length = struct.unpack(">HHH", raw_bytes[:6])

        apid = p_id & 0x07FF
        seq_flags = (p_seq >> 14) & 0x03
        seq_count = p_seq & 0x3FFF
        data_length = length + 1

        return {
            "version": (p_id >> 13) & 0x07,
            "type": (p_id >> 12) & 0x01,
            "sec_hdr": (p_id >> 11) & 0x01,
            "apid": apid,
            "seq_flags": seq_flags,
            "seq_count": seq_count,
            "payload": raw_bytes[6 : 6 + data_length],
        }


class SpaceWireProtocol:
    """
    ECSS-E-ST-50-12C SpaceWire Packet Protocol implementation.
    Structure: Logical Address (1 byte) | Protocol ID (1 byte) | Payload | CRC (1 byte)
    """

    @staticmethod
    def calculate_crc8(data: bytes) -> int:
        """
        Calculates standard CRC-8 checksum over packet bytes.
        """
        crc = 0x00
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x07  # Generator polynomial x^8 + x^2 + x^1 + 1
                else:
                    crc <<= 1
                crc &= 0xFF
        return crc

    @staticmethod
    def create_spw_packet(
        logical_address: int, protocol_id: int, payload: bytes
    ) -> bytes:
        header = struct.pack("BB", logical_address, protocol_id)
        packet_no_crc = header + payload
        crc = SpaceWireProtocol.calculate_crc8(packet_no_crc)
        return packet_no_crc + struct.pack("B", crc)

    @staticmethod
    def parse_spw_packet(raw_bytes: bytes) -> dict:
        if len(raw_bytes) < 3:
            raise ValueError("Buffer too short for SpaceWire packet.")

        logical_address, protocol_id = struct.unpack("BB", raw_bytes[:2])
        payload = raw_bytes[2:-1]
        received_crc = raw_bytes[-1]

        calculated_crc = SpaceWireProtocol.calculate_crc8(raw_bytes[:-1])
        crc_ok = received_crc == calculated_crc

        return {
            "logical_address": logical_address,
            "protocol_id": protocol_id,
            "payload": payload,
            "received_crc": received_crc,
            "crc_ok": crc_ok,
        }


class CANAerospaceProtocol:
    """
    CAN Aerospace 2.0B Frame Parser.
    Frame: 29-bit CAN Identifier | Data Payload (up to 8 bytes)
    Nodal thermal telemetry IDs are mapped to 0x700 to 0x70F.
    """

    @staticmethod
    def pack_can_thermal_telemetry(node_id: int, temp: float, power: float) -> tuple:
        """
        Packs thermal data into a CAN 2.0B 29-bit ID and 8-byte payload.
        ID = 0x700 + (node_id & 0x0F)
        """
        can_id = 0x700 + (node_id & 0x0F)
        # Payload: Float temperature (4 bytes) + Float power (4 bytes)
        payload = struct.pack("<ff", temp, power)
        return can_id, payload

    @staticmethod
    def unpack_can_frame(can_id: int, payload: bytes) -> dict:
        if len(payload) < 8:
            raise ValueError("CAN Payload too short for telemetry packet.")

        node_id = can_id - 0x700
        temp, power = struct.unpack("<ff", payload[:8])

        return {"node_id": node_id, "temperature": temp, "power_w": power}


class CubeSatSpaceProtocol:
    """
    CubeSat Space Protocol (CSP) commands over Port 15 (Active Thermal Service).
    Commands:
    - 0x01: CSP_THERMAL_PREDICT
    - 0x02: CSP_THERMAL_STATUS
    - 0x03: CSP_THROTTLE
    """

    @staticmethod
    def create_csp_command(command_code: int, value: float) -> bytes:
        # Header: Source Port (5 bits) | Dest Port (5 bits) | Command (6 bits)
        # Simplified CSP header: 2 bytes
        header = (15 << 11) | (15 << 6) | (command_code & 0x3F)
        payload = struct.pack(">f", value)
        return struct.pack(">H", header) + payload

    @staticmethod
    def parse_csp_response(raw_bytes: bytes) -> dict:
        if len(raw_bytes) < 6:
            raise ValueError("CSP response too short.")

        (header,) = struct.unpack(">H", raw_bytes[:2])
        src_port = (header >> 11) & 0x1F
        dest_port = (header >> 6) & 0x1F
        cmd = header & 0x3F

        (val,) = struct.unpack(">f", raw_bytes[2:6])

        cmd_names = {
            1: "CSP_THERMAL_PREDICT",
            2: "CSP_THERMAL_STATUS",
            3: "CSP_THROTTLE",
        }

        return {
            "src_port": src_port,
            "dest_port": dest_port,
            "command_code": cmd,
            "command_name": cmd_names.get(cmd, "CSP_UNKNOWN"),
            "value": val,
        }
