#!/usr/bin/env python3
"""
Autonomous Spacecraft Thermal OS - Hamming(7,4) ECC Codec
=========================================================
Implements standard Hamming(7,4) error-correcting codes to detect and correct
Single Event Upsets (SEU) in flight computer memory arrays.
"""


class Hamming74Codec:
    """
    Hamming(7,4) Error Correcting Code.
    Encodes 4 bits of data into a 7-bit codeword with 3 parity bits.
    Can detect and correct 1-bit errors.
    """

    @staticmethod
    def encode_nibble(data: int) -> int:
        """
        Encodes a 4-bit integer (0-15) into a 7-bit codeword.
        Data bits are placed at positions 3, 5, 6, 7 (1-indexed).
        Parity bits are at positions 1, 2, 4.
        """
        d1 = (data >> 3) & 0x01
        d2 = (data >> 2) & 0x01
        d3 = (data >> 1) & 0x01
        d4 = data & 0x01

        # Parity equations
        p1 = d1 ^ d2 ^ d4
        p2 = d1 ^ d3 ^ d4
        p3 = d2 ^ d3 ^ d4

        # Pack codeword: p1, p2, d1, p3, d2, d3, d4
        codeword = (
            (p1 << 6) | (p2 << 5) | (d1 << 4) | (p3 << 3) | (d2 << 2) | (d3 << 1) | d4
        )
        return codeword

    @staticmethod
    def decode_nibble(codeword: int) -> tuple:
        """
        Decodes a 7-bit codeword, detects and corrects any 1-bit error.
        Returns: (decoded_4bit_data, error_detected, error_corrected)
        """
        # Unpack codeword bits: c1 to c7
        c1 = (codeword >> 6) & 0x01
        c2 = (codeword >> 5) & 0x01
        c3 = (codeword >> 4) & 0x01
        c4 = (codeword >> 3) & 0x01
        c5 = (codeword >> 2) & 0x01
        c6 = (codeword >> 1) & 0x01
        c7 = codeword & 0x01

        # Check syndromes
        s1 = c1 ^ c3 ^ c5 ^ c7
        s2 = c2 ^ c3 ^ c6 ^ c7
        s3 = c4 ^ c5 ^ c6 ^ c7

        syndrome = (s3 << 2) | (s2 << 1) | s1

        error_detected = False
        error_corrected = False

        if syndrome != 0:
            error_detected = True
            # Syndrome points to the 1-indexed corrupted bit position
            # Bit positions from MSB to LSB:
            # 1: c1, 2: c2, 3: c3, 4: c4, 5: c5, 6: c6, 7: c7
            # In python shift, the bit index is (7 - position)
            error_bit_index = 7 - syndrome

            # Flip the corrupted bit to correct it
            codeword ^= 1 << error_bit_index
            error_corrected = True

            # Re-extract corrected data bits
            c3 = (codeword >> 4) & 0x01
            c5 = (codeword >> 2) & 0x01
            c6 = (codeword >> 1) & 0x01
            c7 = codeword & 0x01

        # Reconstruct 4-bit data from corrected data bits c3, c5, c6, c7
        decoded_data = (c3 << 3) | (c5 << 2) | (c6 << 1) | c7
        return decoded_data, error_detected, error_corrected


if __name__ == "__main__":
    print("Testing Hamming(7,4) ECC Codec...")
    data = 12  # 1100 binary
    encoded = Hamming74Codec.encode_nibble(data)
    print(f"  Original Data: {bin(data)} | Encoded Codeword: {bin(encoded)}")

    # Inject 1-bit error (flip bit 4 -> position 3 in python shift)
    corrupted = encoded ^ (1 << 3)
    print(f"  Corrupted:     {bin(corrupted)} (1-bit flip injected)")

    decoded, err_det, err_corr = Hamming74Codec.decode_nibble(corrupted)
    print(
        f"  Decoded:       {bin(decoded)} | Error Detected: {err_det} | Error Corrected: {err_corr}"
    )
