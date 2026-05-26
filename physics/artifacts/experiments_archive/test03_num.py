import numpy as np
from scipy.linalg import hilbert

H = hilbert(5)
b = np.ones(5)
try:
    x = np.linalg.solve(H, b)
    print("Numérico Linear Algebra:")
    print(x)
except Exception as e:
    print(f"Error: {e}")
