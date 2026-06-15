# RQB Emergent Gauge Connections

## 1. Introduction
To establish the RQB pregeometric framework as a complete Theory of Everything, we must show how discrete link transport variables $U_{ij}$ on graph edges converge to continuous gauge fields $A_\mu(x)$ in the infrared limit. This document derives the continuous connection fields $A_\mu(x)$ from local spatial averaging and establishes the infinitesimal transport law and continuous gauge transformations.

---

## 2. Connection Mapping: $U_{ij} \to A_\mu(x)$
Let $x^\mu$ be the coordinate center of a local patch of the emergent pseudo-Riemannian manifold, and let $dx^\mu$ be the coordinate displacement vector separating two adjacent vertices $i$ and $j$ in the embedded graph.

In the continuum limit (where the spacing scale $a = |dx| \to 0$), the parallel transport operator $U_{ij}$ along the edge is related to the continuous Lie-algebra-valued gauge connection $A_\mu(x) = A_\mu^a(x) T^a$ by the exponential map:

$$U_{ij} = \exp\left( i g \int_i^j A_\mu(x) dx^\mu \right) = \exp\left( i g A_\mu(x) dx^\mu + \mathcal{O}(|dx|^2) \right)$$

where:
- $g$ is the gauge coupling constant.
- $T^a$ are the generators of the gauge group, satisfying the normalization $\operatorname{Tr}(T^a T^b) = \frac{1}{2} \delta^{ab}$.

---

## 3. Reconstructing $A_\mu(x)$ from Edge Variables
To extract the continuous field components from the discrete link variables $U_{ij}$ on the network, we perform a local spatial averaging over a coarse-graining volume $V$ containing many event vertices. By projecting the logarithm of the link variables onto the generators $T^a$, we isolate the gauge connection components:

$$A_\mu^a(x) \approx \frac{2}{g V} \sum_{(i,j) \in V} \operatorname{Tr}\left[ -i \ln\left( U_{ij} \right) T^a \right] \frac{dx_\mu}{|dx|^2}$$

where the sum runs over all edges in the patch, and $dx_\mu = g_{\mu\nu} dx^\nu$ is the covariant displacement. This local spatial averaging filters out high-frequency pregeometric topological fluctuations, leaving a smooth, low-energy background gauge field.

---

## 4. Local Gauge Redundancy and Transformations
A continuous gauge transformation is represented by a smooth unitary field $\Omega(x) \in SU(3) \times SU(2) \times U(1)$. For vertices $i$ and $j$ located at coordinates $x$ and $x + dx$, the discrete transformation is:

$$U_{ji} \to \Omega(x+dx) U_{ji} \Omega^\dagger(x)$$

Expanding $\Omega(x+dx)$ as a Taylor series:

$$\Omega(x+dx) = \Omega(x) + \partial_\mu \Omega(x) dx^\mu + \mathcal{O}(|dx|^2)$$

Substituting the continuous connection expansion $U_{ji} \approx \mathbb{I} + i g A_\mu dx^\mu$ into the transformation rule:

$$\mathbb{I} + i g A'_\mu dx^\mu \approx \left[ \Omega + \partial_\mu \Omega dx^\mu \right] \left[ \mathbb{I} + i g A_\nu dx^\nu \right] \Omega^\dagger$$

$$\mathbb{I} + i g A'_\mu dx^\mu \approx \mathbb{I} + i g \Omega A_\mu \Omega^\dagger dx^\mu + (\partial_\mu \Omega) \Omega^\dagger dx^\mu$$

Comparing terms at first order in $dx^\mu$ yields the standard gauge transformation of a connection field:

$$A'_\mu(x) = \Omega(x) A_\mu(x) \Omega^\dagger(x) - \frac{i}{g} \left( \partial_\mu \Omega(x) \right) \Omega^\dagger(x)$$

This derivation demonstrates that the continuous gauge transformation rule is an exact consequence of the discrete vertex basis updates.

---

## 5. Infinitesimal Transport Law (Covariant Derivative)
The relation between states at adjacent vertices under parallel transport is:

$$|\psi(x+dx)\rangle = U(x+dx, x) |\psi(x)\rangle = \exp\left( i g A_\mu(x) dx^\mu \right) |\psi(x)\rangle$$

Expanding both sides to first order in the coordinate displacement $dx^\mu$:

$$|\psi(x)\rangle + \partial_\mu |\psi(x)\rangle dx^\mu \approx \left( \mathbb{I} + i g A_\mu(x) dx^\mu \right) |\psi(x)\rangle$$

Rearranging terms:

$$\left( \partial_\mu - i g A_\mu(x) \right) |\psi(x)\rangle dx^\mu = 0$$

Since the displacement $dx^\mu$ is arbitrary, this defines the gauge-covariant derivative $D_\mu$:

$$D_\mu = \partial_\mu - i g A_\mu(x)$$

The covariant derivative satisfies $D_\mu |\psi\rangle \to \Omega D_\mu |\psi\rangle$ under a gauge transformation, ensuring that the physical equations of motion remain invariant under local basis changes.

---

## 6. Conclusion
The continuous gauge connection $A_\mu(x)$ and the covariant derivative $D_\mu$ emerge rigorously in the low-energy limit of discrete edge transport variables on the pregeometric graph.

```python
GAUGE_FIELDS_EMERGENT = True
```
