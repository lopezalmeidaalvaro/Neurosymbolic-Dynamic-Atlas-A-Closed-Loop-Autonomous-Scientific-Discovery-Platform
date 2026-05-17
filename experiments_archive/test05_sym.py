import sympy as sp

x, y = sp.symbols('x y')
f1 = x + y - 2
f2 = x - y
f3 = x**2 + y**2 - 5

G = sp.groebner([f1, f2, f3], x, y)
print("Bases de Gröbner:")
print(list(G))
