import sympy as sp

def isolate_real_roots():
    x = sp.Symbol('x')
    p = x**5 + 3*x**4 - 2*x**3 + 7*x**2 - x + 1
    
    # Sympy's real_roots uses Sturm or similar isolation internally
    real_roots = sp.real_roots(p)
    print(f"Número de raíces reales encontradas: {len(real_roots)}")
    
    for i, root in enumerate(real_roots):
        val = root.evalf()
        print(f"Raíz Real {i+1}: aprox {val} (Representación exacta: {root})")

if __name__ == "__main__":
    isolate_real_roots()
