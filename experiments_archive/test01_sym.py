import sympy as sp

x = sp.Symbol('x')
eq = x**6 - 4*x**5 + 2*x**4 - 7*x**3 + x**2 - x + 3
roots = sp.solve(eq, x)
print("Simbólico exacto:")
for r in roots:
    print(r)
