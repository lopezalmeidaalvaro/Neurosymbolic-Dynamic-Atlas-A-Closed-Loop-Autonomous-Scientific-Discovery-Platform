import scipy.optimize as opt
import numpy as np

def solve_newton_complex():
    print("--- RAMA C: Aproximación Compleja de Newton-Raphson Iterativo ---")
    # P(x) = x^5 - x + 1
    # P'(x) = 5x^4 - 1
    def f(x): return x**5 - x + 1
    def df(x): return 5*x**4 - 1
    
    # Semillas iniciales en el plano complejo (círculo de radio 1.2)
    guesses = [np.exp(2j * np.pi * k / 5) * 1.2 for k in range(5)]
    roots = []
    
    for i, guess in enumerate(guesses):
        try:
            root = opt.newton(f, guess, fprime=df, maxiter=1000, tol=1e-12)
            # Redondeamos para filtrar duplicados por precisión flotante
            root_rounded = np.round(root, decimals=10)
            if not any(np.isclose(root, r, atol=1e-10) for r in roots):
                roots.append(root)
        except Exception as e:
            print(f"Fallo convergiendo desde la semilla {guess}: {e}")
            
    print("\nRaíces únicas convergidas:")
    for i, r in enumerate(roots):
        print(f"Raíz {i+1}: {r}")

    print("\nComprobación de error (P(x)):")
    for i, val in enumerate(roots):
        error = f(val)
        print(f"Error Raíz {i+1}: {np.abs(error)}")

if __name__ == "__main__":
    solve_newton_complex()
