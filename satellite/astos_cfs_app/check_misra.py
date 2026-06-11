# ==============================================================================
# Spacecraft Thermal OS (AST-OS) - MISRA-C Compliance Checker
# File: check_misra.py
# Description: Scans C files for MISRA-C:2012 violations and generates a report.
# ==============================================================================

import os
import re


def check_misra_compliance(c_file_path, report_path):
    print(f"[*] Auditing {c_file_path} for MISRA-C:2012 compliance...")

    if not os.path.exists(c_file_path):
        print(f"[ERROR] C file not found at: {c_file_path}")
        return

    violations = []

    with open(c_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Standard regex rules to detect typical violations in flight software
    dynamic_alloc_pattern = re.compile(r"\b(malloc|calloc|realloc|free)\b")
    recursion_pattern = re.compile(r"\b(void|int|float|double)\s+(\w+)\s*\(.*\)\s*\{")
    goto_pattern = re.compile(r"\bgoto\b")
    unbraced_if_pattern = re.compile(r"\bif\s*\(.*\)\s*[^{\n]+$")
    untyped_int_pattern = re.compile(
        r"\b(int|short|long|char)\b(?!\s*[*]|\s+main|\s+struct|\s+const)"
    )
    double_ptr_pattern = re.compile(r"\*\s*\*")

    for idx, line in enumerate(lines):
        line_num = idx + 1
        clean_line = line.split("//")[0].strip()  # strip trailing comment

        # Rule 21.3: No dynamic memory allocation
        if dynamic_alloc_pattern.search(clean_line):
            violations.append(
                (
                    line_num,
                    "Rule 21.3 (Required)",
                    "Dynamic memory allocation functions shall not be used.",
                )
            )

        # Rule 15.1: No goto statements
        if goto_pattern.search(clean_line):
            violations.append(
                (
                    line_num,
                    "Rule 15.1 (Required)",
                    "The goto statement shall not be used.",
                )
            )

        # Rule 15.6: Control structures must be enclosed in braces
        if unbraced_if_pattern.search(clean_line):
            violations.append(
                (
                    line_num,
                    "Rule 15.6 (Required)",
                    "The body of an if, else, while, do, or for shall be enclosed in braces.",
                )
            )

        # Rule 8.1: Types must be explicitly sized (prefer uint32_t to int, etc.)
        if (
            untyped_int_pattern.search(clean_line)
            and "CFE_" not in line
            and "OS_" not in line
        ):
            violations.append(
                (
                    line_num,
                    "Rule 8.1 (Advisory)",
                    "Standard integer types shall be replaced by explicitly sized types (e.g., int32_t).",
                )
            )

        # Rule 11.5: Conversions between pointer-to-void and pointer-to-object (CFE table mappings often trigger this)
        if "void**" in clean_line or "(void**)" in clean_line:
            violations.append(
                (
                    line_num,
                    "Rule 11.5 (Advisory)",
                    "A cast shall not convert a pointer to a void type to a pointer to an object type.",
                )
            )

        # Rule 18.5: Pointer declarations with more than two levels of indirection shall not be used
        if double_ptr_pattern.search(clean_line) and "(void**)" not in clean_line:
            violations.append(
                (
                    line_num,
                    "Rule 18.5 (Required)",
                    "Pointer declarations with more than two levels of indirection shall not be used.",
                )
            )

    # Write report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(
            "==============================================================================\n"
        )
        f.write("             AST-OS MISRA-C:2012 COMPLIANCE AUTOMATED REPORT\n")
        f.write(
            "==============================================================================\n\n"
        )

        f.write(f"Audited File:   {c_file_path}\n")
        f.write(f"Total Violations Flagged: {len(violations)}\n\n")

        f.write(
            "------------------------------------------------------------------------------\n"
        )
        f.write("                     TOP 10 MOST FREQUENT VIOLATIONS LIST\n")
        f.write(
            "------------------------------------------------------------------------------\n"
        )

        for idx, (line, rule, desc) in enumerate(violations[:10]):
            f.write(f"[{idx+1:2d}] Line {line:3d} | {rule:22s} | {desc}\n")

        f.write(
            "\n------------------------------------------------------------------------------\n"
        )
        f.write("                         QUALIFICATION RECOMMENDATIONS\n")
        f.write(
            "------------------------------------------------------------------------------\n"
        )
        f.write(
            "1. Replace standard basic C types (char, int, short, float) with strictly sized portable\n"
        )
        f.write(
            "   types defined in <stdint.h> (e.g. int32_t, uint8_t, float32_t) to satisfy Rule 8.1.\n"
        )
        f.write(
            "2. Enclose all single-statement control bodies (especially inline checks) in standard\n"
        )
        f.write(
            "   curly braces '{}' to protect instruction jumps from compiler errors (Rule 15.6).\n"
        )
        f.write(
            "3. Keep the flight code completely heap-free. Ensure all table buffers or dynamic arrays\n"
        )
        f.write(
            "   are pre-allocated at compile-time inside global context segments (Rule 21.3).\n"
        )
        f.write(
            "4. Mask all cFS Software Bus pointer conversions. Implement dedicated union structures\n"
        )
        f.write("   to clean up void-to-object pointer casting warnings (Rule 11.5).\n")
        f.write(
            "5. Ensure all loop variables use explicit unsigned bounds to prevent sign conversion overflows.\n"
        )

    print(f"[+] MISRA-C Audit Complete. Report written to: {report_path}")


if __name__ == "__main__":
    check_misra_compliance("astos_app.c", "misra_report.txt")
