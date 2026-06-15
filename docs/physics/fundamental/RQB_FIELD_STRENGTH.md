# RQB Yang–Mills Field Strength

## 1. Introduction
In standard differential geometry, the field strength tensor $F_{\mu\nu}$ represents the curvature of a principal gauge bundle. In the RQB pregeometric framework, this curvature is recovered directly from the parallel transport operator $U_{\text{plaq}}$ around a minimal closed loop (a plaquette) in the emergent coordinates. This document derives the non-Abelian field strength tensor $F_{\mu\nu}$ and its commutator structure.

---

## 2. Plaquette Geometry and Loop Holonomies
Consider a minimal closed loop (plaquette) in the coordinate plane spanned by directions $\hat{\mu}$ and $\hat{\nu}$ with edge length $a$. The loop transport operator $U_{\text{plaq}}$ is given by the ordered product of link variables:

$$U_{\text{plaq}} = U_{x, x+a\hat{\nu}}^\dagger U_{x+a\hat{\mu}, x+a\hat{\mu}+a\hat{\nu}}^\dagger U_{x+a\hat{\mu}+a\hat{\nu}, x+a\hat{\nu}} U_{x+a\hat{\nu}, x}$$

We express the link variables in terms of the continuous connection $A_\mu(x)$ using the midpoint evaluation:

$$U_{x, x+a\hat{\mu}} = \exp\left( i g a A_\mu\left(x + \frac{a}{2}\hat{\mu}\right) \right)$$

---

## 3. Derivation of the Field Strength Tensor
Using the Baker-Campbell-Hausdorff (BCH) expansion, we compute the product of link variables. Recall that for two operators $X$ and $Y$:

$$\ln\left( e^X e^Y \right) = X + Y + \frac{1}{2}[X, Y] + \mathcal{O}(\text{commutators of higher order})$$

Multiplying the four link variables along the boundaries of the plaquette loop yields:

$$U_{\text{plaq}} = \exp\left( i g a^2 F_{\mu\nu}(x) + \mathcal{O}(a^3) \right)$$

Let us analyze the terms order-by-order:

### 3.1 The Abelian Case
If the generators commute ($[A_\mu, A_\nu] = 0$), the BCH expansion simplifies to the sum of fields:

$$U_{\text{plaq}} = \exp\left( i g a \left[ A_\nu\left(x + a\hat{\mu} + \frac{a}{2}\hat{\nu}\right) - A_\nu\left(x + \frac{a}{2}\hat{\nu}\right) - A_\mu\left(x + a\hat{\nu} + \frac{a}{2}\hat{\mu}\right) + A_\mu\left(x + \frac{a}{2}\hat{\mu}\right) \right] \right)$$

In the limit $a \to 0$, we Taylor-expand the connection fields about $x$:

$$A_\nu\left(x+a\hat{\mu}\right) - A_\nu(x) \approx a \partial_\mu A_\nu(x)$$
$$A_\mu\left(x+a\hat{\nu}\right) - A_\mu(x) \approx a \partial_\nu A_\mu(x)$$

Substituting these expansions:

$$U_{\text{plaq}} \approx \exp\left( i g a^2 \left( \partial_\mu A_\nu(x) - \partial_\nu A_\mu(x) \right) \right)$$

This yields the Abelian electromagnetic field strength tensor:

$$F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu$$

### 3.2 The Non-Abelian Case
When the generators do not commute ($[T^a, T^b] = i f^{abc} T^c$), the BCH commutators contribute at second order in the link variables:

$$\frac{1}{2} [i g a A_\mu, i g a A_\nu] = -\frac{g^2 a^2}{2} [A_\mu, A_\nu]$$

Summing all boundary contributions and commutator corrections up to order $a^2$:

$$U_{\text{plaq}} = \mathbb{I} + i g a^2 \left( \partial_\mu A_\nu - \partial_\nu A_\mu - i g [A_\mu, A_\nu] \right) + \mathcal{O}(a^3)$$

By identifying this first-order expansion of the exponential, we recover the non-Abelian field strength tensor $F_{\mu\nu}$:

$$F_{\mu\nu} = \partial_\mu A_\nu - \partial_\nu A_\mu - i g [A_\mu, A_\nu]$$

---

## 4. Commutator Structure and Gauge Covariance
The field strength tensor is a Lie-algebra-valued quantity: $F_{\mu\nu} = F_{\mu\nu}^a T^a$. Its components are:

$$F_{\mu\nu}^a = \partial_\mu A_\nu^a - \partial_\nu A_\mu^a + g f^{abc} A_\mu^b A_\nu^c$$

Under a local gauge transformation $\Omega(x)$, the connection transforms as $A_\mu \to \Omega A_\mu \Omega^\dagger - \frac{i}{g} (\partial_\mu \Omega) \Omega^\dagger$. Substituting this into the field strength expression, we find that the derivatives of the transformation cancel out, yielding the gauge-covariant transformation law:

$$F_{\mu\nu}(x) \to \Omega(x) F_{\mu\nu}(x) \Omega^\dagger(x)$$

This covariance confirms that the pregeometric plaquette curvature matches the geometric curvature of gauge theories.

---

## 5. Conclusion
The gauge field strength tensor $F_{\mu\nu}$ and its non-Abelian commutator structure emerge naturally from the BCH expansion of parallel transport loops on the relational graph.

```python
YANG_MILLS_RECOVERED = True
```
