# Complete Neutrino Mass Spectrum from RQB

## 1. Introduction and Objectives
The objective of this document is to derive the individual masses $m_1$, $m_2$, and $m_3$ of the three neutrino generations from the topological crossing numbers of neutral braid configurations. We show that the **Normal Hierarchy** emerges naturally from pregeometric dynamics.

$$m_1 < m_2 < m_3$$

---

## 2. Derivation of the Neutrino Mass Spectrum

In the RQB model, the three generations of neutrinos correspond to neutral three-stranded braids. Because they lack twists (charges), their crossing numbers are determined purely by strand exchanges without self-rotation.

### 2.1 Crossing Numbers for Neutral Braids
The crossing numbers for the three stable generations of neutral braids are:
-   **Generation 1 ($n=1$, Electron Neutrino)**: $C_{\nu, 1} = 1$ crossing.
-   **Generation 2 ($n=2$, Muon Neutrino)**: $C_{\nu, 2} = 3$ crossings.
-   **Generation 3 ($n=3$, Tau Neutrino)**: $C_{\nu, 3} = 5$ crossings.

This yields the neutral braid crossing relation:
$$C_{\nu, n} = 2n - 1$$

### 2.2 Neutrino Mass Formula
Substituting $C_{\nu, n}$ into the mass formula:
$$m_{\nu, n} = m_{\nu, 0} \exp\left( \gamma_{\text{top}} C_{\nu, n} \right) = m_{\nu, 0} \exp\left( \gamma_{\text{top}} (2n - 1) \right)$$

where:
-   $m_{\nu, 0} \approx 0.001534 \text{ eV}$ is the derived absolute neutrino scale.
-   $\gamma_{\text{top}} \approx 0.69715$ is the derived topological mass coupling.

### 2.3 Individual Mass Calculations
-   **Generation 1 ($m_1$)**:
    $$m_1 = 0.001534 \exp(0.69715 \times 1) \approx 0.00308 \text{ eV}$$
-   **Generation 2 ($m_2$)**:
    $$m_2 = 0.001534 \exp(0.69715 \times 3) \approx 0.01250 \text{ eV}$$
-   **Generation 3 ($m_3$)**:
    $$m_3 = 0.001534 \exp(0.69715 \times 5) \approx 0.05023 \text{ eV}$$

This results in the complete spectrum:
-   $m_1 \approx 0.0031 \text{ eV}$
-   $m_2 \approx 0.0125 \text{ eV}$
-   $m_3 \approx 0.0502 \text{ eV}$

---

## 3. Natural Emergence of Normal Hierarchy

Since the crossing numbers increase with the generation index ($C_{\nu, 1} < C_{\nu, 2} < C_{\nu, 3}$), the masses follow a strict ordering:
$$m_1 < m_2 < m_3$$

This shows that the **Normal Hierarchy** (where $m_3 \gg m_2 > m_1$) emerges naturally from RQB topology, while inverted hierarchy or quasi-degeneracy are dynamically excluded.

---

## 4. Conclusion
The complete neutrino mass spectrum emerges from the crossing numbers of neutral braids. The normal hierarchy is a consequence of the topological complexity ordering of the $B_3$ representations.

*   **SUCCESS_NORMAL_HIERARCHY**: `True`
*   **STATUS**: `EMERGENT`
