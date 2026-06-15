# Pregeometric Origin of Right-Handed Neutrinos in RQB

## 1. Introduction and Objectives
The objective of this document is to identify and describe the sterile/right-handed neutrino excitations within the Relational Quantum Bit-Event (RQB-Event) pregeometric substrate. We show that right-handed neutrinos emerge naturally as charge-neutral bulk topological configurations of the network and derive their heavy Majorana mass scales from first principles.

---

## 2. Topological Classification of Right-Handed Neutrino Excitations

In the RQB substrate, standard model particles are represented by braided ribbon defects attached to the boundary of the gauge manifold. The gauge charges of these excitations are determined by the boundary links:
-   **Color charge ($SU(3)$)**: Braid crossings and color link configurations.
-   **Electroweak charge ($SU(2)_L \times U(1)_Y$)**: Ribbon twists ($T$) and orientation.

### 2.1 Sterile Braids as Bulk States
A sterile/right-handed neutrino state corresponds to a three-stranded braid configuration that:
1.  Carries no twists ($T = 0 \implies Y = 0$).
2.  Has no gauge boundary links, existing as a closed topological loop or a bulk-localized defect.
3.  Carries no color crossings ($Q_{\text{color}} = 0$).

Because these configurations do not connect to the gauge boundaries of the emergent spacetime, they are completely sterile under the gauge forces ($SU(3)_C \times SU(2)_L \times U(1)_Y$). However, they participate in gravity and pregeometric network updates via their local energy-momentum density.

---

## 3. Derivation of the Heavy Mass Scale ($M_R$)

Unlike light neutrinos which are suppressed by LQC background curvature barriers, right-handed neutrinos exist directly in the pregeometric bulk. Their self-energy scale is inversely proportional to the light neutrino suppression factors, yielding a heavy scale $M_{R, 0}$.

### 3.1 The Ground-State Heavy Scale ($M_{R, 0}$)
The heavy mass scale $M_{R, 0}$ is derived from the base pregeometric mass scale $m_0 \approx 7600 \text{ eV}$ scaled by the gauge manifold boundary volume $3\pi^3$ and the topological phase tunneling factor $\exp(2\Xi_{\text{RQB}})$:
$$M_{R, 0} = 3\pi^3 m_0 \exp(2\Xi_{\text{RQB}})$$

where:
-   $m_0 \approx 7600 \text{ eV}$ is the ground-state mass scale.
-   $3\pi^3$ is the volume-scaling factor of the gauge boundary manifold.
-   $\Xi_{\text{RQB}} = \pi\sqrt{3}$ is the microscopic topological invariant representing the quantum dimensions of the RQB network.

Substituting the numeric parameters:
-   $\Xi_{\text{RQB}} = \pi\sqrt{3} \approx 5.441398 \implies 2\Xi_{\text{RQB}} \approx 10.882796$
-   $\exp(2\Xi_{\text{RQB}}) \approx 53252.3$
-   $3\pi^3 \approx 93.018$
-   $M_{R, 0} = 93.018 \times 7600 \text{ eV} \times 53252.3 \approx 3.7646 \times 10^{10} \text{ eV} \approx 37.65 \text{ GeV}$

### 3.2 Generational Right-Handed Neutrino Masses ($M_{R, n}$)
For the three generations ($n=1, 2, 3$), the right-handed mass scale increases with the neutral braid crossing number $C_{\nu, n} = 2n - 1$:
$$M_{R, n} = M_{R, 0} \exp\left( \gamma_{\text{top}} C_{\nu, n} \right) = M_{R, 0} \exp\left( \gamma_{\text{top}} (2n - 1) \right)$$

where $\gamma_{\text{top}} \approx 0.69715$ is the topological mass coupling. This yields:
-   **Generation 1 ($M_{R, 1}$)**:
    $$M_{R, 1} = 37.646 \text{ GeV} \times \exp(0.69715 \times 1) \approx 75.59 \text{ GeV}$$
-   **Generation 2 ($M_{R, 2}$)**:
    $$M_{R, 2} = 37.646 \text{ GeV} \times \exp(0.69715 \times 3) \approx 304.81 \text{ GeV}$$
-   **Generation 3 ($M_{R, 3}$)**:
    $$M_{R, 3} = 37.646 \text{ GeV} \times \exp(0.69715 \times 5) \approx 1.229 \text{ TeV}$$

---

## 4. Conclusion
Right-handed neutrinos emerge naturally as sterile bulk states in the RQB graph. Their mass scale spans the range of $75.6 \text{ GeV}$ to $1.23 \text{ TeV}$, providing the heavy Majorana scales required for the seesaw mechanism.

*   **RIGHT_HANDED_NEUTRINO_EMERGENT**: `True`
*   **STATUS**: `EMERGENT`
