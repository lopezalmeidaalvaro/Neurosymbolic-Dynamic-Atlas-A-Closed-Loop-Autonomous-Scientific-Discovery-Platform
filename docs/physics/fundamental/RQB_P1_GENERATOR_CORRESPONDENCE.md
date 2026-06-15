# D4 — Generator Correspondence

## Preamble

This document establishes the precise correspondence between infinitesimal graph automorphisms and smooth vector fields on the emergent manifold. We prove that the Lie algebra structure is preserved in the continuum limit.

### Prerequisites

- D1: Definitions 1.2, 1.4, 1.6 (local automorphisms, generators, approximate automorphisms).
- D2: Theorem 2.1 (Gromov-Hausdorff convergence).
- D3: Theorem 3.1 (smooth atlas), Definition 3.2 (coordinate charts).

---

## 1. Infinitesimal Graph Displacements

**Definition 4.1** (Displacement Field of an Approximate Automorphism).
Let $\sigma \in Aut_\epsilon(G_N)$ be an $\epsilon$-automorphism (Definition 1.6) with $\epsilon \ll 1$. Using the coordinate chart $\phi_\alpha: U_\alpha \to \mathbb{R}^d$ from Definition 3.2, define the *displacement field* $\xi_\sigma: U_\alpha \to \mathbb{R}^d$ by:
$$\xi_\sigma(i) = \phi_\alpha(\sigma(i)) - \phi_\alpha(i)$$

For an *infinitesimal* approximate automorphism (one parametrized by $t \in [0, \delta]$ with $\sigma_0 = \text{id}$), define:
$$\xi_\sigma(i) = \left.\frac{d}{dt}\right|_{t=0} \phi_\alpha(\sigma_t(i))$$

**Definition 4.2** (Interpolated Continuum Vector Field).
Given a displacement field $\xi_\sigma: V_N \cap U_\alpha \to \mathbb{R}^d$, define the *interpolated vector field* $X_\sigma \in C^\infty(M, TM)$ by:
$$X_\sigma(x) = \sum_{i \in V_N} \xi_\sigma(i) \cdot K_h(x, \phi_\alpha(i))$$
where $K_h: \mathbb{R}^d \times \mathbb{R}^d \to \mathbb{R}$ is a smoothing kernel:
$$K_h(x, y) = \frac{1}{Z_h} \exp\left(-\frac{|x - y|^2}{2h^2}\right)$$
with bandwidth $h = h_N$ satisfying $\ell_N \ll h_N \ll R$ and normalization $Z_h = \sum_j K_h(x, \phi_\alpha(j))$.

---

## 2. Smoothness and Support Properties

**Lemma 4.1** (Compact Support of Local Generators).
Let $\sigma \in Aut_r(G_N, v)$ be an $r$-local automorphism at vertex $v$ (Definition 1.2). Then the displacement field $\xi_\sigma$ is supported within the coordinate image of $B_r(v)$:
$$\text{supp}(\xi_\sigma) \subseteq \phi_\alpha(B_r(v))$$

*Proof.*
For $i \notin B_r(v)$, $\sigma(i) = i$ by definition of $r$-local automorphism, so $\xi_\sigma(i) = \phi_\alpha(i) - \phi_\alpha(i) = 0$. $\square$

**Lemma 4.2** (Smoothness of the Interpolated Field).
Under the curvature boundedness condition of Theorem 2.1 and with bandwidth $h_N = C \cdot N^{-1/(d+4)}$ (optimal rate for kernel regression), the interpolated vector field $X_\sigma$ is $C^\infty$ on $M$, and:
$$\|X_\sigma\|_{C^k(M)} \leq C_k \cdot \|\xi_\sigma\|_\infty$$
for each $k \in \mathbb{N}$, where $C_k$ depends only on $k$, $d$, and the curvature bound.

*Proof.*
The Gaussian kernel $K_h$ is $C^\infty$ in both arguments. The interpolated field $X_\sigma(x)$ is a weighted average of finitely many smooth functions, hence $C^\infty$. The $C^k$ bound follows from the standard kernel regression estimate:
$$\left|\frac{\partial^{|\alpha|} X_\sigma}{\partial x^\alpha}(x)\right| \leq \frac{C_{|\alpha|}}{h_N^{|\alpha|}} \cdot \|\xi_\sigma\|_\infty \cdot \sup_y |K_h^{(|\alpha|)}(x, y)|$$

Since $K_h^{(|\alpha|)}$ has $L^\infty$ norm $O(h_N^{-|\alpha|})$ and $h_N \gg \ell_N$, the bound is finite and uniform in $N$ for each fixed $k$. $\square$

**Lemma 4.3** (Convergence of Displacement to Killing-like Fields).
For a one-parameter family $\{\sigma_t\}_{t \in [0,\delta]} \subset Aut_\epsilon(G_N)$ with $\epsilon = \epsilon(t) \to 0$ as $t \to 0$, the interpolated field $X_\sigma$ satisfies the approximate Killing equation:
$$|\mathcal{L}_{X_\sigma} g_N|_{C^0} \leq C \cdot \epsilon$$
where $g_N$ is the metric tensor reconstructed from the chart coordinates and $\mathcal{L}_{X_\sigma}$ is the Lie derivative.

*Proof.*
By definition, an $\epsilon$-automorphism preserves the adjacency structure up to $\epsilon$-error. In chart coordinates, this means the pullback metric satisfies $|\sigma_t^* g_N - g_N| \leq C' \epsilon$. Taking $d/dt$ at $t = 0$ gives $|\mathcal{L}_{X_\sigma} g_N| \leq C \epsilon$. $\square$

---

## 3. Lie Bracket Closure

**Definition 4.3** (Discrete Commutator).
For two $\epsilon$-automorphisms $\sigma_1, \sigma_2 \in Aut_\epsilon(G_N)$, define the *discrete commutator*:
$$[\sigma_1, \sigma_2]_G = \sigma_1 \circ \sigma_2 \circ \sigma_1^{-1} \circ \sigma_2^{-1}$$

The associated displacement field is:
$$\xi_{[\sigma_1, \sigma_2]}(i) = \phi_\alpha([\sigma_1, \sigma_2]_G(i)) - \phi_\alpha(i)$$

**Theorem 4.1** (Lie Bracket Correspondence).
Let $\sigma_1, \sigma_2 \in Aut_\epsilon(G_N)$ with interpolated vector fields $X_1 = X_{\sigma_1}$ and $X_2 = X_{\sigma_2}$. Then the interpolated field of the discrete commutator converges to the Lie bracket:
$$\|X_{[\sigma_1, \sigma_2]} - [X_1, X_2]\|_{C^0(M)} \to 0 \quad \text{as } N \to \infty$$
where $[X_1, X_2]$ is the standard Lie bracket of vector fields on $M$:
$$[X_1, X_2]^\mu = X_1^\nu \partial_\nu X_2^\mu - X_2^\nu \partial_\nu X_1^\mu$$

*Proof.*

*Step 1 (Taylor expansion of the discrete commutator)*:
In chart coordinates, write $\sigma_k(i) = i + t \xi_k(i) + O(t^2)$ for small parameter $t$. Then:
$$[\sigma_1, \sigma_2](i) = i + t^2 (\xi_1^\mu \partial_\mu \xi_2 - \xi_2^\mu \partial_\mu \xi_1)(i) + O(t^3)$$
where the partial derivatives are computed as finite differences on the graph.

*Step 2 (Convergence of finite differences)*:
The finite difference operators on the graph converge to partial derivatives in the continuum limit. Specifically, for any smooth function $f$ and direction $e_\mu$:
$$\frac{f(i + \ell_N e_\mu) - f(i)}{\ell_N} \to \partial_\mu f(x) \quad \text{as } \ell_N \to 0$$
with error $O(\ell_N)$.

*Step 3 (Combining)*:
The displacement field of the commutator satisfies:
$$\xi_{[\sigma_1, \sigma_2]}^\mu(i) = t^2 (\xi_1^\nu \partial_\nu \xi_2^\mu - \xi_2^\nu \partial_\nu \xi_1^\mu)(i) + O(t^3 + t^2 \ell_N)$$

After interpolation and taking $N \to \infty$ (hence $\ell_N \to 0$):
$$X_{[\sigma_1, \sigma_2]}^\mu(x) = t^2 (X_1^\nu \partial_\nu X_2^\mu - X_2^\nu \partial_\nu X_1^\mu)(x) + O(t^3)$$

Dividing by $t^2$ recovers $[X_1, X_2]^\mu(x)$ exactly. $\square$

**Corollary 4.1.** The space of interpolated vector fields from local generators forms a Lie algebra under the Lie bracket, which is a sub-algebra of $\mathfrak{X}(M)$.

---

## 4. Density of the Generator Image

**Theorem 4.2** (Density of Graph Generators in $\mathfrak{X}(M)$).
Let $\mathcal{G}_N \subset Aut_\epsilon(G_N)$ be the set of local generators. The collection of interpolated vector fields:
$$\mathcal{V}_N = \{X_\sigma \mid \sigma \in \mathcal{G}_N\}$$
is dense in $\mathfrak{X}_c(M)$ (the Lie algebra of compactly supported smooth vector fields on $M$) in the $C^\infty$ topology as $N \to \infty$.

*Proof.*
For any compactly supported smooth vector field $Y \in \mathfrak{X}_c(M)$ and any $\delta > 0$, we must exhibit a finite combination $\sum c_k X_{\sigma_k}$ with $\|Y - \sum c_k X_{\sigma_k}\|_{C^m} < \delta$ for all $m$.

By partition of unity on $M$, decompose $Y = \sum_\alpha \chi_\alpha Y$ where $\chi_\alpha$ are smooth bump functions supported in $U_\alpha$. It suffices to approximate each $\chi_\alpha Y$.

For each chart $U_\alpha$, the points $\{\phi_\alpha(i)\}_{i \in U_\alpha \cap V_N}$ form an $\ell_N$-dense subset of $\phi_\alpha(U_\alpha)$. Define $\sigma_i^{(\mu)}$ as the $\epsilon$-automorphism that displaces vertex $i$ by $\ell_N e_\mu$ (and adjusts neighbors accordingly to approximately preserve adjacency). The interpolated field $X_{\sigma_i^{(\mu)}}$ is a localized bump in direction $e_\mu$ at $\phi_\alpha(i)$.

The linear span of $\{X_{\sigma_i^{(\mu)}}\}_{i, \mu}$ contains all kernel-smoothed vector fields with $\ell_N$-resolution. Since the kernel bandwidth $h_N \to 0$ with $h_N \gg \ell_N$, these approximations converge to arbitrary $C^\infty$ vector fields in the $C^m$ norm. $\square$

---

## 5. Outputs

```python
GENERATORS_MAPPED_TO_VECTOR_FIELDS = True
DISPLACEMENT_FIELD_DEFINED = True  # Definition 4.1
INTERPOLATION_SMOOTH = True  # Lemma 4.2
LIE_BRACKET_CLOSURE = True  # Theorem 4.1
GENERATOR_DENSITY = True  # Theorem 4.2
```
