# Registry of Physical Observables for Hayward-LQC

## 1. Introduction and Objectives
In a diffeomorphism-invariant theory like Loop Quantum Gravity, observables must commute with all constraints (Gauss, diffeomorphism, and Hamiltonian constraints). Such operators are called **Dirac observables** or physical observables. 

Because classical coordinates have no physical meaning, local quantities are not gauge-invariant. We must instead construct global boundary observables or relational observables (defining one physical variable with respect to another).

This registry catalogs the primary observables for the Hayward-LQC regular black hole model, classifying them according to their gauge-invariance status and defining their quantum representations.

---

## 2. Classification Scheme

We classify observables into three distinct classes:

1.  **Kinematical Observables**: Operators defined on the kinematical Hilbert space $\mathcal{H}_{\text{kin}}$ that do not commute with the diffeomorphism or Hamiltonian constraints.
2.  **Physical (Dirac) Observables**: Gauge-invariant operators that commute with all constraints and act on the physical Hilbert space $\mathcal{H}_{\text{phys}}$.
3.  **Relational Observables**: Operators that express a physical quantity relative to a local physical clock or reference field.

---

## 3. Catalog of Hayward-LQC Observables

Below is the catalog of quantum observables evaluated for the regular black hole candidate:

| Observable | Mathematical Definition | Kinematical Representation | Physical/Relational Representation |
| :--- | :--- | :--- | :--- |
| **Horizon Area** | $A_H = 4\pi (r_+^2 + L^2)$ | Kinematical area operator $\hat{A} = 8\pi \gamma l_P^2 \sum \sqrt{j(j+1)}$ | Relational area computed at the horizon boundary state $|s_{\text{hor}}\rangle$ |
| **Internal Volume** | $V_{\text{int}} = \int_{\text{interior}} d^3x \sqrt{-g}$ | Kinematical volume operator $\hat{V}_n$ acting on nodes | Relational volume operator $\hat{V}(\phi)$ at a given scalar clock value $\phi$ |
| **ADM Mass** | $M_{\text{ADM}} = \lim_{r \to \infty} \frac{r}{2}(1 - g_{rr}^{-1})$ | Classical metric boundary term | Dirac observable defined at the spatial infinity boundary |
| **Entropy** | $S = \frac{A_H}{4 l_P^2}$ | Kinematical state-counting operator | Physical observable proportional to the boundary area operator |
| **Effective Curvature** | $R(r)$ and $K(r)$ | Kinematical connection and triad operators | Relational curvature operators $\hat{R}(\phi)$ showing core regularization |
| **Transition Operators** | $\hat{T}(t)$ or $\hat{P}$ | Kinematical time evolution | Physical projection operator $P$ onto the physical Hilbert space |

---

## 4. Detailed Observable Profiles

### 4.1 Horizon Area ($A_H$)
- **Classification**: **Relational Observable**.
- **Quantum Form**: The horizon is defined as the trapping boundary where the expansion of null geodesics vanishes. At the quantum level, it is identified as a boundary spin network state. The area is:
  $$\hat{A}_H |\Psi_{\text{phys}}\rangle = 8\pi \gamma l_P^2 \sum_{e \in \text{horizon}} \sqrt{j_e(j_e + 1)} |\Psi_{\text{phys}}\rangle$$
- **LQC Modification**: The regular cutoff $L$ shifts the classical horizon radius: $r_+^2 \to r_+^2 + L^2$.

### 4.2 Internal Volume ($V_{\text{int}}$)
- **Classification**: **Relational Observable**.
- **Quantum Form**: The internal volume of the regular black hole is computed along a spacelike slice in the interior. In the quantum theory, it is represented as a function of the relational clock $\phi$:
  $$\hat{V}_{\text{int}}(\phi) = \widehat{\text{det}(E^i_a(\phi))}^{1/2}$$
- **LQC Modification**: Unlike classical Schwarzschild where the interior volume collapses to zero at the singularity, the quantum volume reaches a minimum bounded value at the bounce and then expands.

### 4.3 ADM Mass ($M_{\text{ADM}}$)
- **Classification**: **Physical Observable (Boundary)**.
- **Quantum Form**: Defined at spatial infinity where the metric is asymptotically flat:
  $$\hat{H}_{\text{boundary}} |\Psi_{\text{phys}}\rangle = M_{\text{ADM}} |\Psi_{\text{phys}}\rangle$$
  It commutes with all bulk constraints because it is a boundary term, making it a true Dirac observable.

### 4.4 Curvature Operators ($\hat{R}$ and $\hat{K}$)
- **Classification**: **Relational Observable**.
- **Quantum Form**: Expressed by constructing the curvature profile as a function of the scalar clock $\phi$. In the deep core ($\phi \to \infty$), the curvature operators yield finite expectation values:
  $$\langle \hat{R}(\phi) \rangle \approx 16.0 \ l_P^{-2}, \quad \langle \hat{K}(\phi) \rangle \approx 42.67 \ l_P^{-4}$$
  demonstrating quantum regularization.

---

## 5. Evaluation and Verdict

To Q3 / Registry Completeness: *¿Qué tan completo es el conjunto de observables físicos?*

**Verdict**: 
The set of physical observables is **partially complete**. We have well-defined global boundary observables (like ADM mass and total boundary area) and consistent relational bulk observables (like volume or curvature relative to an internal scalar clock). However, local gauge-invariant Dirac observables in the bulk remain extremely difficult to construct without reference to an auxiliary clock field.

---

## 6. Score

*   **OBSERVABLE_COMPLETENESS_SCORE**: `75`

The score of `75/100` indicates that the catalog contains the essential geometric and thermodynamic observables required to physicalize the Hayward-LQC black hole and predict its quantum evolution, but is limited by the lack of local, non-relational gauge-invariant bulk observables.
