import numpy as np
from scipy.optimize import root


def eq(x):
    return np.sin(x) - np.log(x)


sol = root(eq, 2.0)
print("Optimization:")
print(f"Success: {sol.success}, x = {sol.x}")
