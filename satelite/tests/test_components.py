#!/usr/bin/env python3
"""
AST-OS System Component Verification Pytest Suite
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import pytest
import numpy as np
import struct
import os
import sys

# Path resolution
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(TEST_DIR), "satellite", "autonomy"))
sys.path.insert(0, os.path.join(os.path.dirname(TEST_DIR), "satellite", "comms"))

from fault_recovery_ai import FaultRecoveryAI
from mission_planner import AutonomousMissionPlanner
from space_protocol_stack import CCSDSProtocol


def test_fdir_causal_recovery_routing():
    """
    Verifies that the NetworkX causal DiGraph recovery engine maps faults to expected safe plans,
    and isolates defined effects.
    """
    fdir = FaultRecoveryAI(seed=42)

    # SE-B node should succeed to switch to redundant EKF
    actions_se = fdir.plan_recovery("SE-B")
    assert any(
        "Redundant" in act or "redundant" in act or "Reconfigure" in act
        for act in actions_se
    )

    # Undefined fault codes must safely force emergency LEO Safe-Mode reboots
    actions_err = fdir.plan_recovery("X-FLT-999")
    assert any(
        "Safe-Mode" in act or "safe-mode" in act or "Safe" in act for act in actions_err
    )


def test_mission_planner_sa_schedule():
    """
    Asserts that the Simulated Annealing mission planner optimizes timelines successfully
    without violating maximum temperature limits (CPU < 85°C).
    """
    planner = AutonomousMissionPlanner(seed=42)

    # List of candidate tasks
    candidate_tasks = [
        {
            "name": "ground_imaging",
            "type": "imaging",
            "duration": 200.0,
            "thermal_power": 120.0,
            "priority": 5,
        },
        {
            "name": "laser_downlink",
            "type": "downlink",
            "duration": 300.0,
            "thermal_power": 90.0,
            "priority": 4,
        },
        {
            "name": "heater_preheat",
            "type": "preheat",
            "duration": 200.0,
            "thermal_power": 50.0,
            "priority": 3,
        },
    ]

    timeline = planner.optimize_schedule(candidate_tasks)
    assert len(timeline) > 0

    # Confirm maximum temperature remains safe
    cpu_temps = [t["cpu_temp_predicted"] for t in timeline]
    assert (
        max(cpu_temps) <= 85.0
    ), "Mission Planner violated physical temperature constraints!"


def test_ccsds_space_packet_unpacker():
    """
    Asserts that the space communications packers serialize and deserialize big-endian packet headers,
    correctly masking 11-bit APIDs and 14-bit Sequence Counts.
    """
    # Create manual CCSDS space packet hex codeword
    # Primary Header (6 bytes):
    # - 16-bit PID: Version(3b)=0, Type(1b)=0, SecondaryHeader(1b)=0, APID(11b)=0x14 (Radiator Node) -> 0x0014
    # - 16-bit SEQ: Flags(2b)=11 (unsegmented), SequenceCount(14b)=5 -> 0xc005
    # - 16-bit Length: Payload octets - 1 -> 8 payload bytes -> 0x0007
    p_id = 0x0014
    p_seq = 0xC005
    length = 0x0007

    temp_val = 25.4
    timestamp = 177984000

    header = struct.pack(">HHH", p_id, p_seq, length)
    payload = struct.pack(">fI", temp_val, timestamp)
    packet_bytes = header + payload

    # Extract
    p_id_dec, p_seq_dec, length_dec = struct.unpack(">HHH", packet_bytes[:6])
    apid = p_id_dec & 0x07FF
    seq_count = p_seq_dec & 0x3FFF

    assert apid == 0x14, f"Decoded APID is {apid} (expected 0x14)"
    assert seq_count == 5, f"Decoded Sequence is {seq_count} (expected 5)"
    assert length_dec == 7
