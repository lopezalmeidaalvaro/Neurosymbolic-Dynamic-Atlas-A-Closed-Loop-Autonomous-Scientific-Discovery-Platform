# Majorana vs Dirac Neutrino Audit in RQB Topology

## 1. Introduction and Objectives
The objective of this document is to evaluate the topological symmetries of neutral RQB braid configurations to determine whether the substrate predicts Majorana or Dirac neutrinos. We analyze orientation-reversal symmetries, graph self-identification sectors, and charge-conjugation structures.

---

## 2. Topological Symmetry Analysis of Neutral Braids

In the RQB model, standard model fermions are represented by three-stranded braided ribbons with axial twists.
-   **Twist ($T$)**: Determines the electric hypercharge ($Y = T/3$).
-   **Crossing Number ($C_n$)**: Determines the generation index and mass.
-   **Chirality (Orientation)**: Determines left- or right-handed Weyl state.

### 2.1 Orientation Reversal and Charge Conjugation ($C$)
The charge-conjugation operator $C$ corresponds to the topological operation of reversing the orientation of the pregeometric ribbon graph:
$$C: T \to -T$$

For charged leptons (such as the electron, $T = -3$), the charge conjugation maps $T = -3 \to +3$, representing the positron ($\Psi^C \neq \Psi$).

For neutrinos, the twist is exactly zero ($T = 0 \implies Y = 0$). Applying the charge conjugation:
$$C: T = 0 \to -0 = 0$$

Since the twist is zero, the charge-conjugation operator leaves the topological twist invariant.

### 2.2 Braid Self-Duality and Self-Identification
The charge-conjugate neutrino braid has the same twist ($T = 0$) and the same crossing structure ($C_{\nu, n}$). Under the continuous deformation (isotopy) of the RQB graph, the left-handed neutral braid and its orientation-reversed counterpart are topologically isotopic up to a local gauge transformation:
$$\Psi^C \cong \Psi$$

This self-duality is a unique property of the neutral $B_3$ braid representations. It implies that active neutrinos and their sterile counterparts are self-dual, meaning they are their own antiparticles:
$$\Psi^C = \Psi$$

This is the definition of a Majorana fermion.

---

## 3. Exclusion of Dirac Neutrinos

For neutrinos to be Dirac particles, there would have to exist a distinct, topologically non-equivalent right-handed state $N_R$ that carries a conserved charge preventing it from identifying with the left-handed state $\nu_L$ under C-conjugation.

However, in the pregeometric RQB substrate:
1.  All gauge charges are topological invariants (twists and crossings).
2.  A sterile state has $Y = 0$, leaving no gauge charge to distinguish $\nu_L^C$ from $N_R$.
3.  The pregeometric updates allow transitions between active and sterile configurations.

Thus, a Dirac neutrino state is topologically unstable and collapses to Majorana self-dual sectors.

---

## 4. Conclusion
Neutrinos are predicted to be fundamentally **Majorana** particles by the pregeometric topology of the RQB substrate, as a direct consequence of the self-duality of neutral ($T = 0$) braid representations under orientation reversal.

*   **MAJORANA_PREDICTION_DETERMINED**: `True`
*   **STATUS**: `DETERMINED`
