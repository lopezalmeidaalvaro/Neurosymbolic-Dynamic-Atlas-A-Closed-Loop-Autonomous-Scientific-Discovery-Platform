# Phase 37.0 - Canonical Variables

## Scope
This reconstruction is observational and derivative. It uses only the Phase 30-36 outputs for the regularized Hayward candidate

$$A(r)=1-\frac{2M_0 r^2}{r^3+2M_0L^2},\qquad L^2=0.75,\qquad L\simeq0.866.$$

The audit does not introduce a new parameter or a new microscopic ansatz. The aim is to identify the minimal canonical data already implied by the static Hayward geometry, the LQC collapse sector, and the effective action reconstruction.

## Fixed prior inputs
- Phase 30: finite core, $R(0)=16.0$, $K(0)=42.67$, de Sitter limit $A(r)\simeq 1-r^2/L^2$.
- Phase 31: two-horizon Hayward black holes are dynamically vulnerable to Cauchy-horizon mass inflation; horizonless remnants are stable.
- Phase 32: homogeneous LQC collapse has a regular bounce at $\rho=\rho_{crit}$.
- Phase 33: inhomogeneous perturbations leave the remnant sector partially stable.
- Phase 34: LQG/LQC compatibility score is 92%.
- Phase 36: the most plausible fundamental support is LQG/LQC, with nonlocal/effective gravitational support also viable.

## A. ADM formulation
In ADM variables the canonical pair is

$$\left(h_{ij},\pi^{ij}\right),\qquad \pi^{ij}=\sqrt{h}(K^{ij}-Kh^{ij}).$$

For the exact static, spherically symmetric Hayward line element the geometric data are reduced by:
- spherical symmetry,
- staticity,
- the gauge choice $g_{tt}g_{rr}=-1$,
- the fixed regularization scale $L\simeq0.866$ inherited from Phases 30 and 36.

The full ADM phase space has two propagating tensor polarizations per spatial point before symmetry reduction. The Hayward candidate itself does not excite those generic modes. In the reduced sector it is described by the mass profile

$$M(r)=\frac{M_0r^3}{r^3+2M_0L^2},$$

with $M_0$ as the remaining macroscopic label once $L$ is fixed.

## B. Ashtekar-Barbero formulation
The Ashtekar-Barbero canonical pair is

$$\left(A^i_a,E^a_i\right),\qquad A^i_a=\Gamma^i_a+\gamma K^i_a.$$

The prior LQG/LQC interpretation maps the regular core to holonomy corrections and a density bound. In spherical symmetry the independent geometric content can be represented by radial and angular triad/connection components:

$$\left(E^x,E^\phi;K_x,K_\phi\right),$$

subject to diffeomorphism and Hamiltonian constraints. For the homogeneous collapse sector this further reduces to the LQC pair

$$\left(a,p_a\right)$$

or equivalently a polymer pair $(v,b)$, where $v$ is proportional to physical volume and $b$ is the conjugate connection/curvature variable.

## C. Minisuperspace efectivo
Phase 32 already supplies the finite-dimensional dynamical sector: homogeneous collapse with an LQC correction

$$H^2=\frac{8\pi}{3}\rho\left(1-\frac{\rho}{\rho_{crit}}\right).$$

The minimal canonical variables are therefore:
- scale factor $a$ or volume $v=a^3$,
- conjugate momentum $p_a$ or polymer connection variable $b$,
- a mass/energy label $M_0$ fixed by the collapse configuration,
- the fixed cutoff $L\simeq0.866$ derived previously.

## Degrees of freedom
The effective degrees of freedom depend on the sector:

| Sector | Physical degrees of freedom | Reducible to finite dynamics? |
| --- | ---: | --- |
| Exact static Hayward solution with fixed $L$ | 1 macroscopic label, $M_0$ | Yes |
| Homogeneous LQC collapse | 1 canonical pair, $(a,p_a)$ or $(v,b)$ | Yes |
| Spherical inhomogeneous collapse | radial field degrees of freedom after constraints | No, except by truncation |
| Full ADM gravity | 2 tensor modes per point | No |

## Persisted results
```python
CANONICAL_DOF_COUNT = {
    "static_fixed_L": "1 macroscopic mass label M0",
    "homogeneous_minisuperspace": "1 canonical pair",
    "spherical_inhomogeneous": "field-theoretic radial sector",
    "full_ADM": "2 local tensor polarizations per spatial point"
}

CANONICAL_STRUCTURE = "finite only in the static or homogeneous effective truncation; field-theoretic for inhomogeneous perturbations"
```

## Answer
The candidate has one effective canonical pair in the homogeneous quantum-collapse sector and one macroscopic parameter in the exact static solution once $L$ is fixed. It is reducible to finite dynamics only in the minisuperspace/remnant audit used in Phases 32 and 36. The inhomogeneous sector remains a constrained field theory.
