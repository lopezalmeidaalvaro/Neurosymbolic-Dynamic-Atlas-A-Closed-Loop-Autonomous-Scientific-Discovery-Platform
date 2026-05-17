import numpy as np
from scipy.optimize import least_squares

def residuals(vars):
    x, y = vars
    return np.array([
        x + y - 2,
        x - y,
        x**2 + y**2 - 5
    ])

res = least_squares(residuals, [0, 0])
print("Least Squares Optimization:")
print(f"Success: {res.success}, x: {res.x}, cost: {res.cost}")
