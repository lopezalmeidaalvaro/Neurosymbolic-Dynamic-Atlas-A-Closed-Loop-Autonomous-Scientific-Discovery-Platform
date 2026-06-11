#!/usr/bin/env python3
"""
Autonomous Spacecraft Thermal OS - Triple Modular Redundancy (TMR) Inference
============================================================================
Runs three redundant model evaluations in parallel, applying majority voting
to eliminate Single Event Upset computation errors.
"""


class TMRInferenceManager:
    """
    Executes Triple Modular Redundancy (TMR) voting over three computational replicas.
    """

    @staticmethod
    def vote_temperatures(
        out_a: float, out_b: float, out_c: float, tolerance: float = 0.5
    ) -> tuple:
        """
        Compares temperature outputs from three computational replicas.
        Enforces a 2-out-of-3 majority vote if one replica diverges due to bit-flips.
        """
        # Calculate differences
        diff_ab = abs(out_a - out_b)
        diff_ac = abs(out_a - out_c)
        diff_bc = abs(out_b - out_c)

        # Cases:
        # 1. All replicas agree
        if diff_ab <= tolerance and diff_ac <= tolerance:
            # Return average of all three
            return (out_a + out_b + out_c) / 3.0, "ALL_REPLICAS_AGREE", -1

        # 2. Replica C diverges (A and B agree)
        if diff_ab <= tolerance:
            return (out_a + out_b) / 2.0, "REPLICA_C_DIVERGED", 2

        # 3. Replica B diverges (A and C agree)
        if diff_ac <= tolerance:
            return (out_a + out_c) / 2.0, "REPLICA_B_DIVERGED", 1

        # 4. Replica A diverges (B and C agree)
        if diff_bc <= tolerance:
            return (out_b + out_c) / 2.0, "REPLICA_A_DIVERGED", 0

        # 5. Total split-brain divergence (none agree)
        return out_a, "TOTAL_SPLIT_BRAIN_CRITICAL", 99


if __name__ == "__main__":
    print("Testing TMR Temperature Voting Engine...")

    # Nominals
    t_a, t_b, t_c = 22.4, 22.45, 22.38
    voted, status, failed_id = TMRInferenceManager.vote_temperatures(t_a, t_b, t_c)
    print(f"  Nominal:  {voted:.2f}°C | Status: {status} | Failed ID: {failed_id}")

    # Corrupted replica C (bit flip makes temperature shoot up to 88.0°C)
    t_a, t_b, t_c = 22.4, 22.45, 88.00
    voted, status, failed_id = TMRInferenceManager.vote_temperatures(t_a, t_b, t_c)
    print(f"  Faulted:  {voted:.2f}°C | Status: {status} | Failed ID: {failed_id}")
