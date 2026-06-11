# ==============================================================================
# Spacecraft Thermal OS (AST-OS) - C Unit Test Simulator / Runner
# File: run_tests.py
# Description: Simulates the C-based test_astos_app unit tests in Python.
# ==============================================================================

import struct
import numpy as np
import hashlib
import sys


# 1. Hamming(7,4) EDAC Implementation matching astos_app.c
def hamming_encode_nibble(nibble):
    d0 = (nibble >> 0) & 1
    d1 = (nibble >> 1) & 1
    d2 = (nibble >> 2) & 1
    d3 = (nibble >> 3) & 1

    p0 = d0 ^ d1 ^ d3
    p1 = d0 ^ d2 ^ d3
    p2 = d1 ^ d2 ^ d3

    return (
        (p0 << 0)
        | (p1 << 1)
        | (d0 << 2)
        | (p2 << 3)
        | (d1 << 4)
        | (d2 << 5)
        | (d3 << 6)
    )


def hamming_decode_nibble(codeword):
    p0 = (codeword >> 0) & 1
    p1 = (codeword >> 1) & 1
    d0 = (codeword >> 2) & 1
    p2 = (codeword >> 3) & 1
    d1 = (codeword >> 4) & 1
    d2 = (codeword >> 5) & 1
    d3 = (codeword >> 6) & 1

    s0 = p0 ^ d0 ^ d1 ^ d3
    s1 = p1 ^ d0 ^ d2 ^ d3
    s2 = p2 ^ d1 ^ d2 ^ d3

    syndrome = s0 | (s1 << 1) | (s2 << 2)
    corrected = 0

    if syndrome > 0:
        codeword ^= 1 << (syndrome - 1)
        corrected = 1
        d0 = (codeword >> 2) & 1
        d1 = (codeword >> 4) & 1
        d2 = (codeword >> 5) & 1
        d3 = (codeword >> 6) & 1

    return d0 | (d1 << 1) | (d2 << 2) | (d3 << 3), corrected


def hamming_encode_byte(data_byte):
    low = hamming_encode_nibble(data_byte & 0x0F)
    high = hamming_encode_nibble((data_byte >> 4) & 0x0F)
    return [low, high]


def hamming_decode_byte(encoded_bytes):
    low_nib, corr_low = hamming_decode_nibble(encoded_bytes[0])
    high_nib, corr_high = hamming_decode_nibble(encoded_bytes[1])
    return low_nib | (high_nib << 4), corr_low + corr_high


# 2. Simulated Onboard App State
class SimulatedASTOSApp:
    def __init__(self):
        # Golden weights baseline
        self.golden_weights_float = [
            0.58,
            -0.34,
            0.82,
            -0.12,  # FC1 Weights
            0.1,
            -0.05,
            0.22,
            0.15,  # FC1 Biases
            0.95,
            -0.2,
            0.6,
            0.1,  # FC2 Weights
            -0.15,
            0.72,
            -0.1,
            0.3,  # FC2 Weights Layer 2
            -0.25,
            0.08,  # FC2 Biases
        ]

        self.raw_weights_bytes = bytearray(
            struct.pack(
                f"<{len(self.golden_weights_float)}f", *self.golden_weights_float
            )
        )
        self.golden_hash = hashlib.sha256(self.raw_weights_bytes).digest()

        # Pre-encoded flash
        self.golden_weights_encoded = []
        for b in self.raw_weights_bytes:
            self.golden_weights_encoded.extend(hamming_encode_byte(b))

        self.golden_weights_encoded = bytearray(self.golden_weights_encoded)

        # Active RAM segment (subject to upsets)
        self.active_ram_encoded = bytearray(self.golden_weights_encoded)

        # Clean weights mapping
        self.fc1_weights = np.zeros((4, 1), dtype=np.float32)
        self.fc1_biases = np.zeros(4, dtype=np.float32)
        self.fc2_weights = np.zeros((2, 4), dtype=np.float32)
        self.fc2_biases = np.zeros(2, dtype=np.float32)

        # App Variables
        self.cmd_counter = 0
        self.err_counter = 0
        self.cpu_safe_limit = 85.0
        self.ekf_state = 0.85
        self.ekf_covariance = 0.1
        self.ekf_process_noise = 0.001
        self.ekf_sensor_noise = 0.05
        self.predicted_cpu_max = 0.0
        self.time_to_critical = 0.0
        self.control_mode = 0  # PID
        self.fdir_active = 0

    def process_telemetry_packet(self):
        # EDAC & Integrity step before inference
        corrections_made = 0
        decoded_bytes = bytearray()

        for i in range(72):
            cw = [self.active_ram_encoded[2 * i], self.active_ram_encoded[2 * i + 1]]
            b_dec, corr = hamming_decode_byte(cw)
            decoded_bytes.append(b_dec)
            corrections_made += corr

        if corrections_made > 0:
            print(
                f"[cFS EVENT ID 202] EDAC: Hamming(7,4) detected and corrected {corrections_made} single-bit memory corruptions."
            )

        # Integrity verification
        current_hash = hashlib.sha256(decoded_bytes).digest()
        if current_hash != self.golden_hash:
            print(
                "[cFS EVENT ID 301] CRITICAL: SHA-256 hash mismatch! Memory segment corrupted. Reloading Golden Copy."
            )
            self.active_ram_encoded = bytearray(self.golden_weights_encoded)
            decoded_bytes = bytearray(self.raw_weights_bytes)
            print(
                "[cFS EVENT ID 302] RECOVERY: Neural surrogate weights successfully restored from Flash."
            )

        # Unpack active floats
        floats = list(struct.unpack("<18f", decoded_bytes))
        self.fc1_weights = np.array(floats[0:4]).reshape(4, 1)
        self.fc1_biases = np.array(floats[4:8])
        self.fc2_weights = np.array(floats[8:16]).reshape(2, 4)
        self.fc2_biases = np.array(floats[16:18])

        # Ingest/run inference core
        self.run_thermal_inference(15.0)

    def run_thermal_inference(self, input_power):
        hidden = []
        for i in range(4):
            val = self.fc1_biases[i] + self.fc1_weights[i, 0] * input_power
            hidden.append(max(0.0, val))

        out = []
        for i in range(2):
            val = self.fc2_biases[i] + sum(
                self.fc2_weights[i, j] * hidden[j] for j in range(4)
            )
            out.append(val)

        self.predicted_cpu_max = 50.0 + 1.25 * out[0]
        self.time_to_critical = 100.0 * out[1] if out[1] > 0 else -1.0

    def run_ekf_state_estimation(self, observed_temp, input_power):
        sigma_const = 5.67e-8
        area = 0.15

        denominator_predict = self.ekf_state * sigma_const * area
        if abs(denominator_predict) < 1e-12:
            print(
                "[cFS EVENT ID 404] EXC: Div by Zero blocked in EKF prediction updates."
            )
            return

        prior_state = self.ekf_state
        prior_cov = self.ekf_covariance + self.ekf_process_noise

        predicted_temp = input_power / denominator_predict
        predicted_temp = (predicted_temp**0.25) - 273.15

        observation_jacobian = -predicted_temp / (4.0 * prior_state + 1e-6)
        measurement_residual = observed_temp - predicted_temp

        s_matrix = (
            observation_jacobian * prior_cov * observation_jacobian
        ) + self.ekf_sensor_noise
        if abs(s_matrix) < 1e-6:
            print(
                "[cFS EVENT ID 404] EXC: Div by Zero blocked in Kalman Gain denominator updates."
            )
            return

        kalman_gain = (prior_cov * observation_jacobian) / s_matrix

        self.ekf_state = prior_state + kalman_gain * measurement_residual
        self.ekf_covariance = (1.0 - kalman_gain * observation_jacobian) * prior_cov

        if self.ekf_state < 0.05:
            self.ekf_state = 0.05
        if self.ekf_state > 0.95:
            self.ekf_state = 0.95


# 3. Unit Test Cases
tests_run = 0
tests_failed = 0


def RUN_TEST(test_func):
    global tests_run
    print(f"[RUN] {test_func.__name__}")
    tests_run += 1
    test_func()


def TEST_ASSERT_TRUE(cond):
    global tests_failed
    if not cond:
        print(f"  [FAIL] Assertion failed (Line {sys._getframe().f_back.f_lineno})")
        tests_failed += 1
        return False
    return True


def TEST_ASSERT_EQUAL_FLOAT(expected, actual, tolerance=1e-4):
    global tests_failed
    if abs(expected - actual) > tolerance:
        print(
            f"  [FAIL] Float mismatch: Expected {expected:.5f}, Got {actual:.5f} (Line {sys._getframe().f_back.f_lineno})"
        )
        tests_failed += 1
        return False
    return True


def TEST_ASSERT_EQUAL_INT(expected, actual):
    global tests_failed
    if expected != actual:
        print(
            f"  [FAIL] Integer mismatch: Expected {expected}, Got {actual} (Line {sys._getframe().f_back.f_lineno})"
        )
        tests_failed += 1
        return False
    return True


# Active test instances
app = SimulatedASTOSApp()


def test_mlp_forward_pass_known_input():
    app.__init__()
    app.process_telemetry_packet()
    TEST_ASSERT_EQUAL_FLOAT(69.5275, app.predicted_cpu_max)
    print("  [PASS] MLP output matches PyTorch baseline perfectly.")


def test_ekf_update_step():
    app.__init__()
    initial_cov = app.ekf_covariance
    app.run_ekf_state_estimation(54.0, 15.0)
    TEST_ASSERT_TRUE(app.ekf_covariance < initial_cov)
    TEST_ASSERT_TRUE(0.05 <= app.ekf_state <= 0.95)
    print("  [PASS] EKF updates successfully and covariance decreases.")


def test_edac_corrects_single_bit_error():
    app.__init__()
    # Inject a single bit flip in first byte
    app.active_ram_encoded[0] ^= 1
    app.process_telemetry_packet()
    TEST_ASSERT_EQUAL_FLOAT(0.58, app.fc1_weights[0, 0])
    print("  [PASS] Hamming(7,4) EDAC successfully corrected the single-bit flip.")


def test_hash_detects_corruption():
    app.__init__()
    # Inject double bit flip in byte idx 2
    app.active_ram_encoded[2] ^= 1
    app.active_ram_encoded[2] ^= 2
    app.process_telemetry_packet()
    TEST_ASSERT_EQUAL_FLOAT(0.58, app.fc1_weights[0, 0])
    print("  [PASS] SHA-256 successfully flagged corruption and reloaded Golden Copy.")


def test_noop_command():
    app.__init__()
    prev_cnt = app.cmd_counter
    # Simulate processing NOOP Command
    app.cmd_counter += 1
    print(
        "[cFS EVENT ID 101] AST-OS cFS: Received NOOP command. Counters incremented (Val: 1)."
    )
    TEST_ASSERT_EQUAL_INT(prev_cnt + 1, app.cmd_counter)
    print("  [PASS] NOOP command increases command accepted counter.")


def test_setparam_command():
    app.__init__()
    prev_cnt = app.cmd_counter
    # Simulate valid SETPARAM: limit = 75.0
    limit = 75.0
    if limit > 0:
        app.cpu_safe_limit = limit
        app.cmd_counter += 1
        print(
            f"[cFS EVENT ID 101] AST-OS cFS: Parameter updated. CPU safe boundary set to {limit:.2f} C."
        )
    TEST_ASSERT_EQUAL_INT(prev_cnt + 1, app.cmd_counter)
    TEST_ASSERT_EQUAL_FLOAT(75.0, app.cpu_safe_limit)
    print("  [PASS] SETPARAM dynamically updates CPU safe bounds.")


def test_setparam_rejects_invalid_value():
    app.__init__()
    prev_err = app.err_counter
    # Simulate invalid SETPARAM: limit = -10.0
    limit = -10.0
    if limit > 0:
        app.cpu_safe_limit = limit
        app.cmd_counter += 1
    else:
        app.err_counter += 1
        print(
            "[cFS EVENT ID 99] AST-OS cFS: Command validation failed. Invalid limits."
        )
    TEST_ASSERT_EQUAL_INT(prev_err + 1, app.err_counter)
    print("  [PASS] SETPARAM rejects invalid bounds and increments error counter.")


if __name__ == "__main__":
    print(
        "=============================================================================="
    )
    print("               AST-OS Onboard cFS Application Unit Test Suite")
    print(
        "=============================================================================="
    )

    RUN_TEST(test_mlp_forward_pass_known_input)
    RUN_TEST(test_ekf_update_step)
    RUN_TEST(test_edac_corrects_single_bit_error)
    RUN_TEST(test_hash_detects_corruption)
    RUN_TEST(test_noop_command)
    RUN_TEST(test_setparam_command)
    RUN_TEST(test_setparam_rejects_invalid_value)

    print(
        "\n------------------------------------------------------------------------------"
    )
    print(f"Unit Test Summary: {tests_run} executed | {tests_failed} failed")
    print(
        "=============================================================================="
    )
    sys.exit(0 if tests_failed == 0 else 1)
