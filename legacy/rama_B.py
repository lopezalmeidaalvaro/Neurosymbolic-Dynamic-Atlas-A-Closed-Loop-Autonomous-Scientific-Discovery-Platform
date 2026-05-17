import sympy as sp

def solve_symbolic():
    print("--- RAMA B: Aislamiento Simbólico y Representación Algebraica (SymPy) ---")
    x = sp.Symbol('x')
    poly = x**5 - x + 1
    print(f"Polinomio: {poly}")
    
    try:
        print("\nIntentando sp.solve() (Resolución analítica directa)...")
        sol = sp.solve(poly, x)
        print("Solución sp.solve:", sol)
        if not sol:
            print("SymPy no pudo encontrar una solución analítica explícita.")
    except Exception as e:
        print("Error/Excepción en sp.solve:", e)
        
    print("\nUsando representación CRootOf (exacta sobre Q y aproximación arbitraria):")
    try:
        roots = sp.Poly(poly).all_roots()
        for i, r in enumerate(roots):
            print(f"Raíz {i+1} (Exacta): {r}")
            print(f"Raíz {i+1} (Aprox 30 dec): {r.evalf(30)}")
    except Exception as e:
        print("Error obteniendo CRootOf:", e)

if __name__ == "__main__":
    solve_symbolic()
