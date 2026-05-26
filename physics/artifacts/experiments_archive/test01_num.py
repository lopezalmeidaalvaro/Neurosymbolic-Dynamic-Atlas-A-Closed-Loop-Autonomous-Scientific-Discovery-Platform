import numpy as np

coeffs = [1, -4, 2, -7, 1, -1, 3]
roots = np.roots(coeffs)
print("Numérico iterativo:")
for r in roots:
    print(r)
