# Reporte Cuantitativo de Telemetría (Stress Testing Heurístico)

| Problem ID | Framework | Core Functions Used | Status | Exec Time | Information Gain (0-10) | Redundancy Note |
|---|---|---|---|---|---|---|
| test_01_poly | symbolic_exact | `sympy.solve` | SUCCESS | 0.79s | 8 | Raíces exactas representadas (CRootOf), alto coste. |
| test_01_poly | numeric_iterative | `numpy.roots` | SUCCESS | 0.17s | 9 | Muy rápido y efectivo para polinomios densos. |
| test_02_transc | symbolic_exact | `sympy.solve` | SUCCESS (Error manejado) | 1.36s | 3 | Error esperado (`NotImplementedError`), fuerza pivote numérico. |
| test_02_transc | optimization | `scipy.optimize.root` | SUCCESS | 3.21s | 8 | Encontró la raíz eficientemente ($x \approx 2.219$). |
| test_03_illcond | linear_algebra | `numpy.linalg.solve` | SUCCESS | 0.41s | 6 | Rápido, pero susceptible a la inestabilidad de la matriz de Hilbert. |
| test_03_illcond | symbolic_exact | `sympy.Matrix.LUsolve` | SUCCESS | 0.59s | 10 | Solución racional exacta inmune al mal condicionamiento. |
| test_04_dioph | constraint_solver | `itertools.product` (brute) | SUCCESS (No sol) | 1.40s | 4 | Acotó la inexistencia de soluciones en el rango $[-100, 100]$. |
| test_04_dioph | symbolic_exact | `sympy.solvers.diophantine` | SUCCESS (Error manejado) | 0.55s | 2 | Limitaciones en SymPy para cúbicas complejas de 3 variables. |
| test_05_overconst | groebner | `sympy.groebner` | SUCCESS | 0.60s | 10 | Retornó `[1]`, probando concluyentemente que el sistema es inconsistente. |
| test_05_overconst | optimization | `scipy.optimize.least_squares` | SUCCESS | 0.53s | 5 | Retornó un mínimo con `cost > 0`, indicando inconsistencia empíricamente. |

---

### Análisis Heurístico

**¿Qué funciones (ej. `solve()`) demostraron ser frágiles o propensas al TIMEOUT?**
- `sympy.solve()` es frágil frente a ecuaciones trascendentales mixtas (`sin(x) = log(x)`) lanzando `NotImplementedError`, lo que obliga a la heurística a prever bloques `try/except`.
- `sympy.solvers.diophantine()` demostró incapacidad nativa para lidiar con el clásico problema de la suma de tres cubos, denotando que la rama simbólica para teoría de números no lineal está severamente restringida.
- La aproximación de fuerza bruta (`itertools`) consumió bastante tiempo (1.40s) para un grid muy pequeño ($200^3 \approx 8$ millones de iteraciones), por lo que escalar este método garantizaría un `TIMEOUT` seguro sin optimización nativa (Numba/C++).

**¿Qué enfoque ofreció la mejor relación (Information Gain / Exec Time)?**
- **Bases de Gröbner (`sympy.groebner`)** demostró ser el rey absoluto para sistemas sobrestringidos polinomiales. En solo 0.60s logró un _Information Gain_ de 10 al reducir el sistema inconsistente a la base trivial `[1]`, brindando certeza matemática incontestable (frente a la ambigüedad del residuo no nulo de `least_squares`).
- Alternativamente, **`numpy.roots()`** para polinomios densos fue inmensamente más rápido y entregó todas las soluciones explícitas al instante (0.17s frente a los 0.79s de `sympy.solve`).
- Finalmente, **`sympy.Matrix.LUsolve()`** ofreció una relación fantástica para matrices mal condicionadas (Hilbert), blindando el cálculo contra catástrofes de punto flotante por un coste computacional marginal (0.59s).
