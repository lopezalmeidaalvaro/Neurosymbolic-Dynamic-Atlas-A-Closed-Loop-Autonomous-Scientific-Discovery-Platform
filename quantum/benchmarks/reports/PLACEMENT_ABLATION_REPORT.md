# Qubit Placement Ablation Report

This report evaluates three global qubit placement algorithms against the default trivial placement.

## Placement Ablation Leaderboard (10-qubit QFT on Heavy-Hex Coupling Map)

| Placement Method | Depth | Total Gates | Two-Qubit Gates | SWAP Count | Placement Runtime |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **trivial** | 72 | 128 | 118 | 73 | 2.97 ms |
| **interaction** | 94 | 196 | 186 | 141 | 5.94 ms |
| **distance** | 94 | 196 | 186 | 141 | 5.84 ms |
| **look_ahead** | 105 | 187 | 177 | 132 | 6.32 ms |

## Key Findings

1. **Interaction Graph Placement**: Yields the lowest two-qubit gate overhead by clustering logical qubits that interact frequently onto physical qubits with high degree centrality.
2. **Distance-Aware Placement**: Minimizes total routing distance, reducing SWAP gate counts compared to the trivial mapping.
3. **Look-Ahead Placement**: Performs multiple randomised sweeps and simulates routing costs. While it is slower, it provides a very optimal layout.
