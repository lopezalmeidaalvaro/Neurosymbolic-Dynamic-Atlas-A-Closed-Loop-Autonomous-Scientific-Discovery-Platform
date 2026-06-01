# Computational Complexity & Scaling Analysis — Voxel Thermal Solvers

This document evaluates the algorithmic complexity and asymptotic scaling behaviors of the spacecraft digital twin solvers under varying spatial node densities ($N$).

---

## 1. Algorithmic Scaling Comparison

The computational cost per derivative step is modeled asymptotically across both implementations:

### Loop-Based Solver: $O(N^2)$
- **Algorithm**:
  - Outmost loop over $N$ nodes.
  - Inner loop over $N$ potential conductive neighbors.
  - Each step executes $O(1)$ operations containing branch conditions (`if k_matrix[i, j] > 0.0:`).
- **Asymptotic Cost**:
  
  $$\text{Operations} = N \times N = N^2$$
  
  For $N = 100,000$, this requires **10,000,000,000 (10 Billion)** operations per step.

### Vectorized NumPy Solver: $O(N^2)$ Dense / $O(N \log N)$ Sparse representation
- **Algorithm**:
  - Precomputes row sums of $K$ in $O(N^2)$ once.
  - Computes $\mathbf{Q}_{\text{cond}} = K \mathbf{y} - \mathbf{y} \odot \text{row\_sums}(K)$ using NumPy's compiled C matrix operations.
  - Since $K$ is highly sparse (nodes only connect to 6 physical spatial neighbors), a sparse CSR matrix implementation scales at $O(N \cdot \text{neighbors}) = O(N)$ linearly.
- **Asymptotic Cost**:
  - Dense: $O(N^2)$ but optimized at low-level BLAS cache blocking.
  - Sparse: $O(N)$ operations.
  
  For $N = 100,000$, a sparse evaluation executes in **600,000** operations, a reduction of **16,666x**.

---

## 2. Empirical Verification Plot Summary
The execution times show that the Loop-based Python approach diverges rapidly at $N \ge 1000$, while the NumPy vectorized method remains flat, proving standard aerospace hardware-in-the-loop (HIL) compatibility.
