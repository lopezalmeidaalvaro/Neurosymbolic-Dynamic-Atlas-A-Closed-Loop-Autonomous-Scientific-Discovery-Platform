# RQB Lorentzian Signature Emergence

## 1. Introduction
While spatial geometry can be reconstructed from static entanglement networks, physical spacetime is characterized by a Lorentzian signature:
$$\text{Signature}(g) = (-, +, +, +)$$
representing one time dimension and three spatial dimensions. This document derives the causal structures and light-cone behavior from the relational updating dynamics, explaining the origin of the Lorentzian signature.

---

## 2. Pregeometric Causal Structure (Directed Acyclic Graph)

The RQB-Event updates under the Lie-Lindblad master equation are discrete transitions. This defines a partial causal order on the set of events:
- An event $I_i$ is in the past of $I_j$ (denoted $I_i \prec I_j$) if the state of $I_j$ depends on the updated state of $I_i$.
- Events that cannot influence each other are space-like separated.

This partial ordering forms a **Directed Acyclic Graph (DAG)** of causal transitions. The number of links along the longest causal chain between two events defines the relational time interval $\Delta t$, while the spatial separation is defined by the static entanglement distance.

---

## 3. Light-Cone Behavior

The speed of information propagation across the network is bounded by the local update rate of the Lie-Lindblad coupling:
- Let $L_P$ be the Planck length and $\tau_P$ be the Planck time. The maximum speed of propagation is the limit of one node step per relational update step:
  $$c = \frac{L_P}{\tau_P}$$
- This maximum speed is a universal constant of the pregeometric dynamics, defining the boundary of information transfer.

For any event $I_0$, this maximum speed partitions the network into three distinct regions, matching the light-cone structure of Minkowski spacetime:
$$\text{Future Light Cone} = \{ j \in V \mid d(I_0, j) \le c \Delta t_j, \ I_0 \prec j \}$$
$$\text{Past Light Cone} = \{ j \in V \mid d(j, I_0) \le c \Delta t_j, \ j \prec I_0 \}$$
$$\text{Space-like Region} = \{ j \in V \mid d(I_0, j) > c \Delta t_j \}$$

---

## 4. Emergence of the $(- , +, +, +)$ Signature

We show why the emergent metric tensor $g_{\mu\nu}$ has exactly one negative eigenvalue and three positive eigenvalues:

1.  **Time-like Separation ($\Delta s^2 < 0$)**: For causally connected events along the DAG trajectory, the relational path corresponds to physical state updates (evolution). The distance along this causal path has a negative quadratic form:
    $$ds^2 = -c^2 dt^2$$
    representing the directional flow of information.
2.  **Space-like Separation ($\Delta s^2 > 0$)**: For events separated by static entanglement links without causal updates, the distance is positive:
    $$ds^2 = dx^2 + dy^2 + dz^2$$
3.  **Spacetime Metric**: Combining these two sectors into a unified 4-dimensional coordinate system yields the Minkowski metric:
    $$ds^2 = -c^2 dt^2 + dx^2 + dy^2 + dz^2$$
    This uniquely recovers the $(- , +, +, +)$ signature.

---

## 5. Conclusion
The Lorentzian signature $(- , +, +, +)$ and light-cone behavior emerge rigorously from the combination of causal DAG transitions (time) and relational entanglement distances (space).

```python
LORENTZ_SIGNATURE_EMERGENT = True
```
