# Quantitative Neutrino predictions from RQB

## 1. Introduction and Objectives
The objective of this document is to generate new, falsifiable quantitative experimental predictions for the neutrino sector from the pregeometric RQB derivations. These predictions provide testable signatures for future cosmological and laboratory experiments.

---

## 2. Experimental predictions

Using the derived neutrino masses ($m_1 \approx 0.0031 \text{ eV}$, $m_2 \approx 0.0125 \text{ eV}$, $m_3 \approx 0.0502 \text{ eV}$) and PMNS mixing angles, we predict:

### 2.1 Sum of Neutrino Masses ($\sum m_\nu$)
The total sum of neutrino masses is a key observable in cosmology (constrained by cosmic microwave background and large-scale structure measurements):
$$\sum m_\nu = m_1 + m_2 + m_3 \approx 0.00308 + 0.01250 + 0.05023 \approx 0.0658 \text{ eV}$$

Therefore, we predict:
$$\sum m_\nu \approx 0.0658 \text{ eV}$$

This value is just above the minimum possible limit for the normal hierarchy ($\approx 0.06 \text{ eV}$) and is testable by the EUCLID satellite and DESI galaxy surveys.

### 2.2 Effective Mass in Beta Decay ($m_\beta$)
The effective mass measured in direct beta decay searches (such as the tritium decay of KATRIN and Project 8):
$$m_\beta = \sqrt{|U_{e1}|^2 m_1^2 + |U_{e2}|^2 m_2^2 + |U_{e3}|^2 m_3^2}$$

Using the perturbed PMNS elements ($|U_{e1}|^2 \approx 0.674$, $|U_{e2}|^2 \approx 0.303$, $|U_{e3}|^2 \approx 0.023$):
$$m_\beta \approx \sqrt{0.674 (0.00308)^2 + 0.303 (0.0125)^2 + 0.023 (0.0502)^2} \approx \sqrt{6.39 \times 10^{-6} + 4.73 \times 10^{-5} + 5.8 \times 10^{-5}} \approx 0.0106 \text{ eV}$$

Therefore, we predict:
$$m_\beta \approx 0.0106 \text{ eV}$$

### 2.3 Effective Mass in Neutrinoless Double Beta Decay ($m_{\beta\beta}$)
The effective mass governing neutrinoless double beta decay ($0\nu\beta\beta$), assuming light Majorana exchange:
$$m_{\beta\beta} = \left| \sum U_{ei}^2 m_i \right| \approx \left| |U_{e1}|^2 m_1 + |U_{e2}|^2 m_2 e^{i\alpha_1} + |U_{e3}|^2 m_3 e^{i\alpha_2} \right|$$

With minimal CP phases, we obtain:
$$m_{\beta\beta} \approx 0.674 (0.00308) + 0.303 (0.0125) \approx 0.00207 + 0.00378 \approx 0.0059 \text{ eV}$$

Therefore, we predict:
$$m_{\beta\beta} \approx 0.0059 \text{ eV}$$

This lies in the discovery region of future ultra-sensitive searches like LEGEND-1000 and nEXO.

### 2.4 Leptonic CP Phase ($\delta_{\text{CP}}$)
The CP-violating phase of the PMNS matrix is predicted from the topological background phase $\delta_{\text{topo}} = \pi/15$:
$$\delta_{\text{CP}} \approx \pi - \theta_{13} \approx 180^\circ - 8.52^\circ \approx 171.5^\circ$$

Therefore, we predict:
$$\delta_{\text{CP}} \approx 171.5^\circ$$

---

## 3. Prediction Ledger

| Observable | Predicted Value | Experimental Status | Test Method / Experiment |
| :--- | :---: | :--- | :--- |
| **$\sum m_\nu$** | $0.0658 \text{ eV}$ | $< 0.12 \text{ eV}$ (Planck Bound) | Cosmology (DESI / EUCLID) |
| **$m_\beta$** | $0.0106 \text{ eV}$ | $< 0.8 \text{ eV}$ (KATRIN) | Tritium Decay (Project 8) |
| **$m_{\beta\beta}$** | $0.0059 \text{ eV}$ | $< 0.03 - 0.09 \text{ eV}$ (KamLAND-Zen) | $0\nu\beta\beta$ (LEGEND / nEXO) |
| **$\delta_{\text{CP}}$** | $171.5^\circ$ | Constrained by T2K/NOvA | Long-baseline Oscillations (DUNE) |

---

## 4. Conclusion
We have derived four new, quantitative, falsifiable neutrino observables from pregeometric RQB network constraints. These predictions are testable by next-generation neutrino physics experiments.

*   **STATUS**: `EMERGENT`
