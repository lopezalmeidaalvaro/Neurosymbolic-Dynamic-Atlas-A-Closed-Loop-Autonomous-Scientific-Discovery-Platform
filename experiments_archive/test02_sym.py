import sympy as sp

x = sp.Symbol('x')
eq = sp.sin(x) - sp.log(x)
try:
    roots = sp.solve(eq, x)
    print("Simbólico exacto:")
    for r in roots:
        print(r)
except NotImplementedError as e:
    print(f"NotImplementedError: {e}")
