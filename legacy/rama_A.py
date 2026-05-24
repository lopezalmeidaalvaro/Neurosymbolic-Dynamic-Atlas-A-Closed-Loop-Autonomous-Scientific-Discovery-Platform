import numpy as np


def solve_companion():
    print("--- RAMA A: Método de la Matriz Acompañante ---")
    # P(x) = x^5 - x + 1 = 0
    # Coeficientes: c_0=1, c_1=-1, c_2=0, c_3=0, c_4=0
    # Matriz acompañante (forma canónica)
    matrix = np.array(
        [
            [0, 0, 0, 0, -1],
            [1, 0, 0, 0, 1],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 1, 0],
        ]
    )
    eigenvalues = np.linalg.eigvals(matrix)
    print("Raíces encontradas (Autovalores):")
    for i, val in enumerate(eigenvalues):
        print(f"Raíz {i+1}: {val}")

    # Comprobación de error
    print("\nComprobación de error (P(x)):")
    for i, val in enumerate(eigenvalues):
        error = val**5 - val + 1
        print(f"Error Raíz {i+1}: {np.abs(error)}")


if __name__ == "__main__":
    solve_companion()
