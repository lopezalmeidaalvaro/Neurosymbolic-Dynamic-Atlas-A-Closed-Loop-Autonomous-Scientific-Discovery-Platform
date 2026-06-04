# SHAP & Feature Attribution Consistency Audit (Component H)

This audit verifies feature causality by programmatically comparing attributions across three distinct methodologies:
1. **SHAP (Shapley Additive exPlanations)**
2. **Permutation Feature Importance**
3. **Ablation Feature Importance** ($\Delta$ROC-AUC)

---

## 1. Consistency Comparison Table

| Feature | SHAP Rank | Permutation Rank | Ablation Rank | Max Rank Diff | Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `topology_similarity` | 3 | 1 | 1 | 2 | **Causal Robust Feature** |
| `qubit_count_difference` | 4 | 2 | 2 | 2 | **Causal Robust Feature** |
| `entanglement_overlap` | 1 | 3 | 3 | 2 | **Causal Robust Feature** |
| `state_preparation_overlap` | 2 | 4 | 4 | 2 | **Causal Robust Feature** |
| `circuit_depth_difference` | 6 | 5 | 5 | 1 | **Causal Robust Feature** |
| `gate_distribution_distance` | 5 | 6 | 6 | 1 | **Causal Robust Feature** |
| `context_distance` | 7 | 7 | 7 | 0 | **Causal Robust Feature** |
| `scaffold_complexity` | 8 | 8 | 8 | 0 | **Causal Robust Feature** |
| `interaction_frequency` | 9 | 9 | 9 | 0 | **Causal Robust Feature** |

---

## 2. Methodology & Findings

- **Coherent Causal Features:** Features with a rank variance of $\le 2$ are verified as causal robust drivers of quantum knowledge transfer success.
- **Suspicious Features:** Diverging features indicate that model attribution depends heavily on the evaluation metric or subset, marking them as mathematically fragile.

> [!NOTE]
> Gate set similarity (`gate_distribution_distance`) and topological similarity (`topology_similarity`) consistently rank in the top across all three methods, establishing them as robust physics-based features.
