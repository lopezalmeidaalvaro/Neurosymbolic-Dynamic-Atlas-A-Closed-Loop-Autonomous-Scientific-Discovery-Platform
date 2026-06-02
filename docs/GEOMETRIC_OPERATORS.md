# Phase 37.0 - Geometric Operators

## Scope
This document reconstructs the geometric operator content compatible with the prior Hayward/LQC evidence.

## Area operator
The LQG-compatible sector supports a nonzero area gap. Phase 36 used the standard LQG motivation that the Hayward cutoff is linked to discrete quantum geometry.

The audit result is:

```python
AREA_GAP = "PRESENT_IN_LQG_LQC_EFFECTIVE_SECTOR"
```

The effective Hayward cutoff $L\simeq0.866$ is not identical to the square root of the standard LQG area gap. It is the radial/core length obtained after matching the central density

$$\rho(0)=\frac{3}{8\pi L^2}$$

to the critical density in the effective collapse model. The comparison is therefore order-Planck compatibility, not equality of spectra.

## Volume operator
In the polymer/LQC homogeneous sector the natural basis is a volume basis $|v\rangle$, so volume is discrete in the effective quantum geometry.

```python
VOLUME_GAP = "PRESENT_IN_MINISUPERSPACE_POLYMER_SECTOR"
```

The prior phases do not compute a full black-hole interior volume spectrum, so the result is restricted to the reduced collapse sector.

## Curvature operator
The effective curvature is bounded by the Hayward core:

$$R(0)=\frac{12}{L^2}=16.0,$$

$$K(0)=\frac{24}{L^4}=42.67.$$

Thus:

```python
CURVATURE_BOUND = {
    "Ricci_scalar_core": 16.0,
    "Kretschmann_core": 42.67,
    "status": "PRESENT_EFFECTIVELY"
}
```

## Comparison with L approximately 0.866
| Quantity | Prior value | Interpretation |
| --- | ---: | --- |
| $L$ | 0.866 | effective radial cutoff/core length |
| $L^2$ | 0.75 | cutoff entering Hayward mass denominator |
| $\Lambda_{eff}$ | 4.0 | central de Sitter cosmological term |
| $R(0)$ | 16.0 | bounded Ricci scalar |
| $K(0)$ | 42.67 | bounded Kretschmann scalar |

## Conclusion
The geometric operator audit supports an area gap and volume discreteness in the LQG/LQC-compatible sector and a direct effective curvature bound in the Hayward geometry. The exact spectral derivation of $L=0.866$ from full geometric operators is not established in the prior phases; the established statement is compatibility through the density-bound matching.
