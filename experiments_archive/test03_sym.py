import sympy as sp

H = sp.Matrix(5, 5, lambda i, j: sp.Rational(1, i + j + 1))
b = sp.Matrix(5, 1, [1, 1, 1, 1, 1])
try:
    x = H.LUsolve(b)
    print("Simbólico exacto:")
    print(x)
except Exception as e:
    print(f"Error: {e}")
