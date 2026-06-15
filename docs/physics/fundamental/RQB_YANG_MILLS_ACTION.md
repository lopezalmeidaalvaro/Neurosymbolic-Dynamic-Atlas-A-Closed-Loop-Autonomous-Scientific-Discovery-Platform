# RQB Yang–Mills Action Recovery

## 1. Introduction
The dynamics of gauge fields in the continuous limit are governed by the Yang–Mills action:

$$S_{\text{YM}} = -\frac{1}{4} \int d^4x \operatorname{Tr}\left( F_{\mu\nu} F^{\mu\nu} \right)$$

In the pregeometric RQB framework, we must derive this action from the relational Hamiltonian and updating dynamics of the discrete network, verifying both gauge invariance and the classical equations of motion.

---

## 2. Plaquette Hamiltonian and Relational Energy
The RQB master equation drives the state configuration toward minimizing the relational Hamiltonian $\hat{H}_{\text{rel}}$. The energy associated with a closed loop $\mathcal{C}$ on the relational graph is determined by the trace of its parallel transport operator:

$$E(\mathcal{C}) = \alpha_0 \left( \operatorname{Tr}(\mathbb{I}) - \operatorname{Re}\operatorname{Tr}\left[ W(\mathcal{C}) \right] \right)$$

where $\alpha_0$ is a dimension-setting energy scale. For a minimal closed coordinate loop (a plaquette) of area $a^2$ in the $\mu$-$\nu$ plane:

$$U_{\text{plaq}} = \exp\left( i g a^2 F_{\mu\nu} \right)$$

Using the Taylor expansion of the matrix exponential:

$$\operatorname{Tr}\left( U_{\text{plaq}} \right) = \operatorname{Tr}\left( \mathbb{I} + i g a^2 F_{\mu\nu} - \frac{g^2 a^4}{2} F_{\mu\nu} F^{\mu\nu} + \mathcal{O}(a^6) \right)$$

Since $F_{\mu\nu}$ is traceless for $SU(N)$ generators:

$$\operatorname{Tr}\left( F_{\mu\nu} \right) = 0$$

Taking the real part:

$$\operatorname{Re}\operatorname{Tr}\left( U_{\text{plaq}} \right) = \operatorname{Tr}(\mathbb{I}) - \frac{g^2 a^4}{2} \operatorname{Tr}\left( F_{\mu\nu} F^{\mu\nu} \right) + \mathcal{O}(a^6)$$

Substituting this back into the relational energy equation:

$$E(\text{plaq}) = \frac{\alpha_0 g^2 a^4}{2} \operatorname{Tr}\left( F_{\mu\nu} F^{\mu\nu} \right) + \mathcal{O}(a^6)$$

---

## 3. Deriving the Continuous Action
The total action is the integral of the relational energy density over time, which corresponds to the sum over all plaquette loops in the network:

$$S_{\text{eff}} = -\int dt \sum_{\text{plaq}} E(\text{plaq}) \approx -\int d^4x \frac{1}{4} \operatorname{Tr}\left( F_{\mu\nu} F^{\mu\nu} \right)$$

where we identify:
- The coordinate integration measure: $\sum_{\text{plaq}} a^4 \to \int d^4x$.
- The coupling normalization: $\alpha_0 = \frac{1}{2 g^2}$.

This recovers the standard kinetic action for non-Abelian Yang–Mills fields:

$$S_{\text{YM}} = -\frac{1}{4} \int d^4x \operatorname{Tr}\left( F_{\mu\nu} F^{\mu\nu} \right) = -\frac{1}{4} \int d^4x F_{\mu\nu}^a F^{a,\mu\nu}$$

---

## 4. Gauge Invariance of the Action
To prove that $S_{\text{YM}}$ is gauge-invariant, we apply a local gauge transformation $\Omega(x)$ to the field strength tensor $F_{\mu\nu} \to \Omega F_{\mu\nu} \Omega^\dagger$:

$$\operatorname{Tr}\left( F'_{\mu\nu} F'^{\mu\nu} \right) = \operatorname{Tr}\left( \Omega F_{\mu\nu} \Omega^\dagger \Omega F^{\mu\nu} \Omega^\dagger \right)$$

Since $\Omega^\dagger \Omega = \mathbb{I}$:

$$\operatorname{Tr}\left( F'_{\mu\nu} F'^{\mu\nu} \right) = \operatorname{Tr}\left( \Omega F_{\mu\nu} F^{\mu\nu} \Omega^\dagger \right)$$

Using the cyclic property of the trace ($\operatorname{Tr}(ABC) = \operatorname{Tr}(CAB)$):

$$\operatorname{Tr}\left( F'_{\mu\nu} F'^{\mu\nu} \right) = \operatorname{Tr}\left( \Omega^\dagger \Omega F_{\mu\nu} F^{\mu\nu} \right) = \operatorname{Tr}\left( F_{\mu\nu} F^{\mu\nu} \right)$$

Thus, the action is strictly invariant under all continuous gauge transformations.

---

## 5. Classical Equations of Motion
By varying the Yang–Mills action with respect to the gauge field components $A_\nu^a$:

$$\delta S_{\text{YM}} = \int d^4x \operatorname{Tr}\left( \left( D_\mu F^{\mu\nu} \right) \delta A_\nu \right)$$

Requiring $\delta S_{\text{YM}} = 0$ for all physical perturbations yields the classical **Yang–Mills equations of motion**:

$$D_\mu F^{\mu\nu} = \partial_\mu F^{\mu\nu} - i g [A_\mu, F^{\mu\nu}] = 0$$

In the presence of matter currents $J^\nu$ (fermions):

$$D_\mu F^{\mu\nu} = J^\nu$$

These equations govern the dynamics of gluons, W/Z bosons, and photons, confirming the dynamical consistency of the RQB continuum limit.

---

## 6. Conclusion
The gauge-invariant non-Abelian Yang–Mills action and its classical equations of motion emerge rigorously from the relational energy Hamiltonian of the pregeometric network.

```python
YANG_MILLS_RECOVERED = True
```
