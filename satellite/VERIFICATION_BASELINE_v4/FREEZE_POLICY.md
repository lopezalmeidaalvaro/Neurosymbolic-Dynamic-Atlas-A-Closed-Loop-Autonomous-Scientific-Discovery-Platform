# Freeze Policy

**Baseline**: `VERIFICATION_BASELINE_v4`  
**Authority**: Configuration Management Lead  
**Date**: 2026-05-31  

---

## Historical Modification Prohibition

`VERIFICATION_BASELINE_v4` is frozen as an immutable historical configuration item.

Rules:

1. Do not modify, replace, delete, normalize, reformat, or regenerate files inside `VERIFICATION_BASELINE_v4`.
2. Do not update evidence in place, even for typographical corrections.
3. Do not refresh hashes in place after freeze.
4. Any later evidence update, correction, re-run, FRR preparation, or release-readiness action must create `VERIFICATION_BASELINE_v5`.
5. `VERIFICATION_BASELINE_v5` must copy forward applicable v4 evidence and document the v4-to-v5 delta.

---

## Enforcement Applied

The baseline is protected by read-only file attributes and SHA-256 hashes recorded in `SHA256SUMS.txt` and `BASELINE_MANIFEST.md`.

