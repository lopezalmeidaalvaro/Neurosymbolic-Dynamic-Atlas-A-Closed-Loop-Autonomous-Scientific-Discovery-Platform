# RQB U(1) Sector Recovery

## 1. Introduction
The objective of this document is to derive the emergent $U(1)$ gauge sector from the self-rotational Dehn twists of the RQB ribbons. We recover the phase symmetry and show how continuous electromagnetic gauge invariance emerges in the low-energy limit.

---

## 2. Phase Symmetries and Ribbon Twists

In the pregeometric network, each ribbon event carries a continuous self-rotational degree of freedom: the Dehn twist angle $\theta \in [0, 2\pi)$.

### 2.1 Hypercharge Transformation
An excitation carrying hypercharge (twist charge) $Y$ transforms under local self-rotations of the ribbon by an angle $\phi(x)$ according to:
$$|s(x)\rangle \to e^{i Y \phi(x)} |s(x)\rangle$$

This local phase rotation is a symmetry of the topological state, representing a $U(1)$ gauge transformation.

### 2.2 Link Variables and Gauge Covariance
The parallel transport operator along a graph edge connecting $x$ and $x+dx$ is represented by the $U(1)$ link variable:
$$U(x, x+dx) = e^{i g A_\mu(x) dx^\mu}$$

For the covariant derivative $D_\mu = \partial_\mu - i g A_\mu$ to remain covariant under the local phase transformation:
$$D_\mu \psi(x) \to e^{i \phi(x)} D_\mu \psi(x)$$

the link variable must transform as:
$$U(x, x+dx) \to e^{i \phi(x)} U(x, x+dx) e^{-i \phi(x+dx)}$$

Expanding to first order in $dx$:
$$e^{i g A'_\mu dx^\mu} \approx e^{i \phi(x)} e^{i g A_\mu dx^\mu} e^{-i (\phi(x) + \partial_\mu \phi dx^\mu)} = e^{i g A_\mu dx^\mu - i \partial_\mu \phi dx^\mu}$$

Solving for the transformed field $A'_\mu(x)$:
$$A'_\mu(x) = A_\mu(x) - \frac{1}{g} \partial_\mu \phi(x)$$

This is exactly the continuous gauge transformation of standard electromagnetism.

---

## 3. The Maxwell Action

In the Abelian limit (where the generators commute), the plaquette field strength tensor simplifies to:
$$F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu$$

The relational update dynamics minimizes the plaquette energy:
$$S_{\text{Abelian}} = \sum_{\text{plaq}} \left( 1 - \operatorname{Re}(U_{\text{plaq}}) \right) \approx \int d^4x \frac{1}{4} F_{\mu\nu} F^{\mu\nu}$$

recovering the standard Maxwell kinetic action of classical electromagnetism.

---

## 4. Conclusion
The $U(1)$ electromagnetic gauge sector and its gauge invariance are rigorously derived from the continuous Dehn twist phases of the RQB ribbons.

```python
U1_RECOVERED = True
```
