import numpy as np

def find_all_roots():
    # p = x**5 + 3*x**4 - 2*x**3 + 7*x**2 - x + 1
    # coeficientes de mayor a menor grado
    coeffs = [1, 3, -2, 7, -1, 1]
    
    roots = np.roots(coeffs)
    print("Todas las raíces (numéricas):")
    for i, r in enumerate(roots):
        print(f" Raíz {i+1}: {r}")
        
    real_roots = [r for r in roots if np.isreal(r) or abs(r.imag) < 1e-10]
    complex_roots = [r for r in roots if abs(r.imag) >= 1e-10]
    
    print(f"\nResumen:")
    print(f" Raíces Reales: {len(real_roots)}")
    print(f" Raíces Complejas: {len(complex_roots)}")

if __name__ == "__main__":
    find_all_roots()
