# Freeze Policy

**Baseline**: `VERIFICATION_BASELINE_v3`  
**Authority**: Configuration Management Lead  
**Date**: 2026-05-31T14:41:02+01:00  

---

## Historical Modification Prohibition

`VERIFICATION_BASELINE_v3` is frozen as an immutable historical configuration item.

Rules:

1. Do not modify, replace, delete, normalize, reformat, or regenerate files inside `VERIFICATION_BASELINE_v3`.
2. Do not update evidence in place, even to correct typographical errors.
3. Do not refresh hashes in place after freeze.
4. Any later evidence update, correction, re-run, or closure activity must create `VERIFICATION_BASELINE_v4`.
5. `VERIFICATION_BASELINE_v4` must copy forward applicable v3 evidence and document the v3-to-v4 delta.

---

## Enforcement Applied

The baseline is protected by:

- read-only file attributes applied after manifest generation
- SHA-256 artifact hashes in `BASELINE_MANIFEST.md`
- full baseline checksums in `SHA256SUMS.txt`
- explicit configuration-control rule requiring version increment for future changes

