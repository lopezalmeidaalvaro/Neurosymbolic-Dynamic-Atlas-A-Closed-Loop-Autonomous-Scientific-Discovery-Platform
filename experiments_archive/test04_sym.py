import sympy as sp
from sympy.solvers.diophantine import diophantine

x, y, z = sp.symbols("x y z", integer=True)
eq = x**3 + y**3 + z**3 - 33
try:
    sols = diophantine(eq)
    print("Simbólico exacto:")
    print(sols)
except NotImplementedError as e:
    print(f"NotImplementedError: {e}")
except Exception as e:
    print(f"Error: {e}")
