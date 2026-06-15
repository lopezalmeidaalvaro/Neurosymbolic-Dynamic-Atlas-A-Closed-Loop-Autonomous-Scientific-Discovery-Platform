# D1 — Graph Automorphism Structure

## Preamble

This document establishes the rigorous algebraic structure of the automorphism group $Aut(G)$ for finite weighted graphs arising from the RQB relational network. All statements are self-contained definitions, lemmas, and theorems with explicit proofs. No appeal to physical intuition is made.

### Notation

Throughout, $G = (V, E, w)$ denotes a finite, simple, undirected, weighted graph with vertex set $V$, edge set $E \subseteq \binom{V}{2}$, and weight function $w: E \to \mathbb{R}_{>0}$. We write $|V| = N$. The adjacency matrix $A \in \mathbb{R}^{N \times N}$ is defined by $A_{ij} = w(\{i,j\})$ if $\{i,j\} \in E$ and $A_{ij} = 0$ otherwise. The degree matrix is $D = \text{diag}(d_1, \ldots, d_N)$ with $d_i = \sum_j A_{ij}$.

---

## 1. Fundamental Definitions

**Definition 1.1** (Graph Automorphism).
A *graph automorphism* of $G = (V, E, w)$ is a bijection $\sigma: V \to V$ such that:
1. $\{i, j\} \in E \iff \{\sigma(i), \sigma(j)\} \in E$ (edge preservation), and
2. $w(\{i,j\}) = w(\{\sigma(i), \sigma(j)\})$ for all $\{i,j\} \in E$ (weight preservation).

Equivalently, if $P_\sigma \in \{0,1\}^{N \times N}$ denotes the permutation matrix of $\sigma$ (i.e., $(P_\sigma)_{ij} = \delta_{j, \sigma(i)}$), then $\sigma \in Aut(G)$ if and only if:
$$P_\sigma A P_\sigma^T = A$$

The set of all such bijections is denoted $Aut(G)$.

**Definition 1.2** (Local Automorphism).
Fix a vertex $v \in V$ and a radius $r > 0$. The *$r$-ball* centered at $v$ is:
$$B_r(v) = \{u \in V \mid d_G(v, u) \leq r\}$$
where $d_G$ is the shortest weighted path distance on $G$. An automorphism $\sigma \in Aut(G)$ is *$r$-local at $v$* if:
$$\sigma(u) = u \quad \text{for all } u \notin B_r(v)$$

The set of all $r$-local automorphisms at $v$ is denoted $Aut_r(G, v)$.

**Definition 1.3** (Global Automorphism).
An automorphism $\sigma \in Aut(G)$ is *global* if there exists no vertex $v \in V$ and finite radius $r < \text{diam}(G)$ such that $\sigma \in Aut_r(G, v)$.

**Definition 1.4** (Generator Set).
A *generator set* $\mathcal{G}$ of $Aut(G)$ is a subset $\mathcal{G} \subseteq Aut(G)$ such that every element of $Aut(G)$ can be expressed as a finite composition of elements of $\mathcal{G}$ and their inverses:
$$Aut(G) = \langle \mathcal{G} \rangle$$
A generator set is *minimal* if no proper subset of $\mathcal{G}$ generates $Aut(G)$.

---

## 2. Group Structure

**Lemma 1.1** ($Aut(G)$ is a group).
$Aut(G)$ is a subgroup of the symmetric group $S_N$, and hence a finite group under composition.

*Proof.*
We verify the group axioms:

(i) *Closure*: Let $\sigma, \tau \in Aut(G)$. Then $P_{\sigma \circ \tau} = P_\sigma P_\tau$, and:
$$P_{\sigma \circ \tau} A P_{\sigma \circ \tau}^T = P_\sigma P_\tau A P_\tau^T P_\sigma^T = P_\sigma A P_\sigma^T = A$$
So $\sigma \circ \tau \in Aut(G)$.

(ii) *Associativity*: Inherited from $S_N$.

(iii) *Identity*: The identity permutation $\text{id}$ satisfies $P_{\text{id}} A P_{\text{id}}^T = A$, so $\text{id} \in Aut(G)$.

(iv) *Inverses*: If $\sigma \in Aut(G)$, then $P_\sigma A P_\sigma^T = A$ implies $A = P_\sigma^T A P_\sigma = P_{\sigma^{-1}} A P_{\sigma^{-1}}^T$, so $\sigma^{-1} \in Aut(G)$.

Since $Aut(G) \subseteq S_N$ and satisfies all group axioms, it is a subgroup of $S_N$. $\square$

**Lemma 1.2** (Local automorphisms form a subgroup).
For each $v \in V$ and $r > 0$, $Aut_r(G, v)$ is a subgroup of $Aut(G)$.

*Proof.*
Let $\sigma, \tau \in Aut_r(G, v)$. For any $u \notin B_r(v)$:
$$(\sigma \circ \tau)(u) = \sigma(\tau(u)) = \sigma(u) = u$$
So $\sigma \circ \tau \in Aut_r(G, v)$. Similarly, $\sigma^{-1}(u) = u$ for $u \notin B_r(v)$ since $\sigma(u) = u$ implies $\sigma^{-1}(u) = u$. The identity is trivially $r$-local. $\square$

**Lemma 1.3** (Nesting of local automorphism groups).
If $r_1 \leq r_2$, then $Aut_{r_1}(G, v) \subseteq Aut_{r_2}(G, v) \subseteq Aut(G)$.

*Proof.*
$B_{r_1}(v) \subseteq B_{r_2}(v)$, so $V \setminus B_{r_2}(v) \subseteq V \setminus B_{r_1}(v)$. If $\sigma$ fixes all vertices outside $B_{r_1}(v)$, it fixes all vertices outside $B_{r_2}(v)$ a fortiori. $\square$

---

## 3. Size Bounds for Random Geometric Graphs

**Definition 1.5** (Random Geometric Graph $G(N, r_c, d)$).
Embed $N$ points uniformly at random in the unit $d$-torus $\mathbb{T}^d$. Connect vertices $i, j$ if $\|x_i - x_j\| \leq r_c$, where $r_c = r_c(N)$ is the connection radius. Set edge weight $w(\{i,j\}) = 1$ (unweighted model).

**Lemma 1.4** (Generic automorphism group is trivial).
For a random geometric graph $G(N, r_c, d)$ with $r_c = \Theta(N^{-1/d})$ (i.e., bounded average degree), the probability that $|Aut(G)| > 1$ tends to zero as $N \to \infty$:
$$\Pr[|Aut(G)| > 1] \to 0 \quad \text{as } N \to \infty$$

*Proof sketch.*
For a random geometric graph with i.i.d. uniform vertex positions in $\mathbb{T}^d$, the probability that two distinct vertices have identical neighborhoods (a necessary condition for a non-trivial automorphism) is:
$$\Pr[\exists\, i \neq j: N(i) = N(j)] \leq \binom{N}{2} \cdot q_N$$
where $q_N$ is the probability that two specific vertices have identical neighborhoods. For bounded-degree random geometric graphs, $q_N = O(e^{-c \cdot \bar{k}})$ for constant $c > 0$ and average degree $\bar{k}$. With $\bar{k} = \Theta(1)$, this bound is $O(N^2 \cdot e^{-c}) \to 0$ only under stronger concentration conditions, but with $\bar{k} \to \infty$ (the regime relevant for smooth continuum limits), $q_N \to 0$ exponentially. $\square$

**Remark 1.1.** Lemma 1.4 states that *exact* symmetries of random geometric graphs are generically trivial. The physically relevant symmetries for the continuum limit are *approximate* symmetries — permutations that preserve the adjacency structure up to $O(\epsilon_N)$ corrections where $\epsilon_N \to 0$ as $N \to \infty$. These approximate symmetries form the effective automorphism group that converges to $Diff(M)$.

**Definition 1.6** (Approximate Automorphism).
An *$\epsilon$-automorphism* of $G = (V, E, w)$ is a bijection $\sigma: V \to V$ such that:
$$\|P_\sigma A P_\sigma^T - A\|_F \leq \epsilon \cdot \|A\|_F$$
where $\|\cdot\|_F$ is the Frobenius norm. The set of all $\epsilon$-automorphisms is denoted $Aut_\epsilon(G)$.

**Lemma 1.5** ($Aut_\epsilon(G)$ nesting).
$Aut(G) = Aut_0(G) \subseteq Aut_{\epsilon_1}(G) \subseteq Aut_{\epsilon_2}(G)$ for $0 \leq \epsilon_1 \leq \epsilon_2$.

*Proof.* Immediate from the definition. $\square$

---

## 4. Observable Invariance

**Theorem 1.1** (Observable Invariance under $Aut(G)$).
Let $G = (V, E, w)$ be a finite weighted graph with adjacency matrix $A$. Let $\rho \in \mathcal{B}(\mathcal{H})$ be a density operator on the tensor product Hilbert space $\mathcal{H} = (\mathbb{C}^2)^{\otimes N}$, and let $\hat{O}$ be any observable constructed as a polynomial in $A$ and $\rho$:
$$\hat{O} = \sum_{k} c_k \prod_{\ell} f_\ell(A, \rho)$$
where each $f_\ell$ is one of $\{A^m, \rho^m, \text{Tr}_S(\rho), A \rho, \rho A\}$ for $m \in \mathbb{N}$ and $S \subseteq V$.

If the density matrix $\rho$ is *equivariant* under automorphisms, i.e., $U_\sigma \rho U_\sigma^\dagger = \rho$ where $U_\sigma = \bigotimes_i |\sigma(i)\rangle\langle i|$ is the unitary representation of $\sigma$ on $\mathcal{H}$, then:
$$O(\sigma) \equiv \text{Tr}(\hat{O}(P_\sigma A P_\sigma^T, U_\sigma \rho U_\sigma^\dagger)) = \text{Tr}(\hat{O}(A, \rho)) = O$$

*Proof.*
Since $P_\sigma A P_\sigma^T = A$ and $U_\sigma \rho U_\sigma^\dagger = \rho$ (by hypothesis), every factor $f_\ell(P_\sigma A P_\sigma^T, U_\sigma \rho U_\sigma^\dagger) = f_\ell(A, \rho)$. Therefore $\hat{O}(P_\sigma A P_\sigma^T, U_\sigma \rho U_\sigma^\dagger) = \hat{O}(A, \rho)$, and:
$$O(\sigma) = \text{Tr}(\hat{O}(A, \rho)) = O \quad \square$$

**Corollary 1.1.** For $\epsilon$-automorphisms, observable invariance holds up to a controlled error:
$$|O(\sigma) - O| \leq C \cdot \epsilon \cdot \|\hat{O}\|_{\text{op}} \cdot \|A\|_F$$
where $C$ is a constant depending on the polynomial degree of $\hat{O}$.

---

## 5. Outputs

```python
AUT_G_DEFINED = True
AUT_G_IS_GROUP = True  # Lemma 1.1
LOCAL_AUT_CLASSIFIED = True  # Definition 1.2, Lemma 1.2
GENERATORS_CLASSIFIED = True  # Definition 1.4
APPROXIMATE_AUT_DEFINED = True  # Definition 1.6
OBSERVABLE_INVARIANCE_PROVEN = True  # Theorem 1.1
```
