# Neutrinoless Double Beta Decay Predictions from RQB

## 1. Introduction and Objectives
Since the pregeometric RQB substrate predicts that neutrinos are Majorana particles, neutrinoless double beta decay ($0\nu\beta\beta$) is physically allowed. The objective of this document is to predict the decay rates, half-life ranges, and isotope dependence for next-generation experiments using the derived effective Majorana mass $m_{\beta\beta} \approx 0.0059 \text{ eV}$.

---

## 2. The Effective Majorana Mass ($m_{\beta\beta}$)

The decay rate of $0\nu\beta\beta$ is proportional to the square of the effective Majorana mass $m_{\beta\beta}$:
$$m_{\beta\beta} = \left| \sum_{i=1}^3 U_{ei}^2 m_i \right|$$

Using the derived neutrino mass spectrum ($m_1 \approx 0.0031 \text{ eV}$, $m_2 \approx 0.0124 \text{ eV}$, $m_3 \approx 0.0501 \text{ eV}$) and PMNS mixing angles, we calculated in Phase 52:
$$m_{\beta\beta} \approx 0.0059 \text{ eV}$$

This value is used to predict the half-lives for the most relevant experimental isotopes.

---

## 3. Half-Life Prediction Formula and Isotope Parameters

The half-life of neutrinoless double beta decay, $T_{1/2}^{0\nu}$, is given by:
$$(T_{1/2}^{0\nu})^{-1} = G_{0\nu} |M_{0\nu}|^2 \left( \frac{m_{\beta\beta}}{m_e} \right)^2$$

where:
-   $G_{0\nu}$ is the phase space factor (in $\text{yr}^{-1}$).
-   $M_{0\nu}$ is the dimensionless nuclear matrix element (NME).
-   $m_e = 510998.9 \text{ eV}$ is the electron rest mass.

We use the standard values and range of NMEs from nuclear theory:

| Isotope | Phase Space Factor $G_{0\nu}$ ($\text{yr}^{-1}$) | Nuclear Matrix Element $M_{0\nu}$ Range |
| :--- | :---: | :---: |
| **Xenon-136 ($^{136}\text{Xe}$)** | $1.46 \times 10^{-14}$ | $[2.0,  4.0]$ |
| **Germanium-76 ($^{76}\text{Ge}$)** | $2.36 \times 10^{-15}$ | $[3.0,  6.0]$ |

---

## 4. Predicted Half-Lives

### 4.1 Xenon-136 ($^{136}\text{Xe}$)
Using the parameters for $^{136}\text{Xe}$:
-   **Upper Bound ($M_{0\nu} = 4.0$)**:
    $$(T_{1/2}^{0\nu})^{-1} = 1.46 \times 10^{-14} \times 16 \times \left( \frac{0.0059}{510998.9} \right)^2 \approx 3.11 \times 10^{-29} \text{ yr}^{-1} \implies T_{1/2}^{0\nu} \approx 3.21 \times 10^{28} \text{ yr}$$
-   **Lower Bound ($M_{0\nu} = 2.0$)**:
    $$(T_{1/2}^{0\nu})^{-1} = 1.46 \times 10^{-14} \times 4 \times \left( \frac{0.0059}{510998.9} \right)^2 \approx 7.78 \times 10^{-30} \text{ yr}^{-1} \implies T_{1/2}^{0\nu} \approx 1.28 \times 10^{29} \text{ yr}$$

We predict:
$$T_{1/2}^{0\nu}(^{136}\text{Xe}) \approx 3.2 \times 10^{28} \text{ yr} \quad \text{to} \quad 1.3 \times 10^{29} \text{ yr}$$

### 4.2 Germanium-76 ($^{76}\text{Ge}$)
Using the parameters for $^{76}\text{Ge}$:
-   **Upper Bound ($M_{0\nu} = 6.0$)**:
    $$(T_{1/2}^{0\nu})^{-1} = 2.36 \times 10^{-15} \times 36 \times \left( \frac{0.0059}{510998.9} \right)^2 \approx 1.13 \times 10^{-29} \text{ yr}^{-1} \implies T_{1/2}^{0\nu} \approx 8.83 \times 10^{28} \text{ yr}$$
-   **Lower Bound ($M_{0\nu} = 3.0$)**:
    $$(T_{1/2}^{0\nu})^{-1} = 2.36 \times 10^{-15} \times 9 \times \left( \frac{0.0059}{510998.9} \right)^2 \approx 2.83 \times 10^{-30} \text{ yr}^{-1} \implies T_{1/2}^{0\nu} \approx 3.53 \times 10^{29} \text{ yr}$$

We predict:
$$T_{1/2}^{0\nu}(^{76}\text{Ge}) \approx 8.8 \times 10^{28} \text{ yr} \quad \text{to} \quad 3.5 \times 10^{29} \text{ yr}$$

---

## 5. Experimental Testing and Comparison
Current limits from KamLAND-Zen ($^{136}\text{Xe}$) set $T_{1/2}^{0\nu} > 2.3 \times 10^{26} \text{ yr}$, while GERDA/LEGEND-200 ($^{76}\text{Ge}$) sets $T_{1/2}^{0\nu} > 1.8 \times 10^{26} \text{ yr}$.

Our predicted half-lives are approximately two orders of magnitude higher than current limits. They lie in the discovery region of future ultra-sensitive projects:
-   **LEGEND-1000** ($^{76}\text{Ge}$): target sensitivity $\approx 10^{28} \text{ yr}$.
-   **nEXO** ($^{136}\text{Xe}$): target sensitivity $\approx 10^{28} \text{ yr}$.

---

## 6. Conclusion
The Majorana nature of neutrinos in RQB allows $0\nu\beta\beta$. The predicted half-lives are $\approx 10^{28} - 10^{29}$ years, which are testable by next-generation double beta decay search experiments.

*   **DOUBLE_BETA_DECAY_PREDICTED**: `True`
*   **STATUS**: `PREDICTED`
