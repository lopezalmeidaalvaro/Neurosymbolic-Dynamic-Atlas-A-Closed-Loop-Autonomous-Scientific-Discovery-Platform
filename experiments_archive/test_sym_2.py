import sympy as sp

x = sp.Symbol("x")
eq = x**4 - 1
roots = sp.solve(eq, x)
print(f"Raices: {roots}")
