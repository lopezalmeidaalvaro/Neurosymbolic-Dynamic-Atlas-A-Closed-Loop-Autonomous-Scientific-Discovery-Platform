# Phase 37.0 - Hamiltonian Audit

## Scope
This audit reconstructs the effective Hamiltonian constraint implied by Phases 30-36. It does not introduce a new Hamiltonian model. The result is an effective, symmetry-reduced Hamiltonian compatible with the observed Hayward core and LQC bounce.

## Classical constraint structure
In canonical gravity the physical states satisfy

$$\hat H\Psi=0.$$

For the homogeneous collapse sector the classical minisuperspace constraint has the schematic form

$$H_{cl}(a,p_a)=T(a,p_a)+U_{GR}(a;\rho),$$

where the kinetic term is quadratic in the canonical momentum and the potential term encodes the attractive GR collapse.

## Effective quantum correction
Phase 32 gives the LQC correction:

$$H^2=\frac{8\pi}{3}\rho\left(1-\frac{\rho}{\rho_{crit}}\right).$$

Therefore the effective Hamiltonian must contain a repulsive contribution that becomes dominant as $\rho\to\rho_{crit}$ and cancels the classical contraction rate at the bounce.

Using the Phase 36 relation

$$\rho(0)=\frac{3}{8\pi L^2}\equiv\rho_{crit},$$

the same correction explains the Hayward de Sitter core

$$A(r)\simeq1-\frac{r^2}{L^2}.$$

## Kinetic terms
The kinetic content is the standard reduced gravitational kinetic term for the scale factor or volume:

$$T\sim -\frac{p_a^2}{a}$$

in WDW language, or a polymerized holonomy kinetic term in LQC:

$$p_a^2\quad\longrightarrow\quad \frac{\sin^2(\lambda b)}{\lambda^2}.$$

No new value of $\lambda$ is fixed here. The only scale retained from prior phases is the effective cutoff $L\simeq0.866$.

## Potential terms
The potential contains:
- the classical attractive collapse term,
- the matter/energy density source associated with $M_0$,
- the effective repulsive LQC factor $(1-\rho/\rho_{crit})$,
- the de Sitter core implied by $\Lambda_{eff}=3/L^2=4.0$.

The Hayward mass function

$$M(r)=\frac{M_0r^3}{r^3+2M_0L^2}$$

is the static geometric expression of this effective potential barrier.

## Does the de Sitter core arise as a ground state?
Within the effective reconstruction, yes: the central state is the finite-curvature vacuum-like configuration with

$$P_r(0)=P_t(0)=-\rho(0),\qquad \Lambda_{eff}=\frac{3}{L^2}.$$

This is not a proof of the exact ground state of full LQG. It is the ground-state structure of the effective geometry already reconstructed in Phases 30 and 36.

## Does an effective repulsive potential exist?
Yes. It is required by three prior results:
- finite $R(0)$ and $K(0)$ in Phase 30,
- homogeneous bounce at $\rho=\rho_{crit}$ in Phase 32,
- LQC effective-action support in Phase 36.

## Persisted results
```python
GROUND_STATE_STRUCTURE = "effective de_Sitter_core_with_rho0_3_over_8pi_L2"

HAMILTONIAN_STATUS = {
    "constraint": "H Psi = 0",
    "kinetic": "ADM/minisuperspace kinetic term, polymerized in LQC sector",
    "potential": "classical attraction plus LQC/Hayward repulsive density bound",
    "status": "EFFECTIVE_RECONSTRUCTION_SUPPORTED"
}
```

## Conclusion
The Hamiltonian audit supports an effective constrained Hamiltonian whose repulsive high-density term produces the Hayward core. The reconstruction is strong in minisuperspace and effective quantum geometry, but it remains an effective Hamiltonian rather than a full nonperturbative operator derivation.
