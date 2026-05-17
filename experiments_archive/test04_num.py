import itertools
import sys

def solve():
    limit = 100
    print(f"Buscando soluciones en el rango [-{limit}, {limit}]...")
    # Brute force
    for x, y, z in itertools.product(range(-limit, limit+1), repeat=3):
        if x**3 + y**3 + z**3 == 33:
            print(f"Solución encontrada: x={x}, y={y}, z={z}")
            return
    print("Ninguna solución encontrada en el rango.")

if __name__ == "__main__":
    solve()
