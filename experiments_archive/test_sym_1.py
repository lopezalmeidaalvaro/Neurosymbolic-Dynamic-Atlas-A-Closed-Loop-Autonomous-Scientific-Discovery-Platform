import sympy as sp

x = sp.Symbol("x")
eq = x**4 - 1
roots = sp.roots(eq, x)
print(f"Raices: {roots}")
