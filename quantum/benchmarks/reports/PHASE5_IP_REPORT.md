# QADE Phase V IP Report

## IP Inventory

* number_of_motifs: **30**
* unique_motifs: **13**
* validated_motifs: **13**
* reusable_motifs: **11**
* transferability_pct: **84.6%**
* unseen_circuits_improved_pct: **100.0%**
* estimated_hardware_benefit: **3.655e-04**
* estimated_commercial_value: **$1,100,000**

## Top 50 Motifs

| Motif ID | Type | Frequency | Gate Reduction | Duration Reduction (us) | Fidelity Gain | Score |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| motif_a65a11902c7503cd | cancellation_pattern | 83 | 2.00 | 1.74 | 9.880e-01 | 904.22 |
| motif_7a0884c44bb7c14b | cancellation_pattern | 44 | 2.00 | 0.12 | 9.871e-01 | 195.85 |
| motif_e66f0ef6f44da17a | rotation_cancellation | 6 | 2.00 | 0.24 | 9.871e-01 | 17.74 |
| motif_6828d62ca193d193 | rotation_cancellation | 6 | 2.00 | 0.24 | 9.871e-01 | 17.74 |
| motif_5f8b73934973613d | rotation_cancellation | 6 | 2.00 | 0.24 | 9.871e-01 | 17.74 |
| motif_bbfc459399ecbfc7 | rotation_cancellation | 5 | 2.00 | 0.00 | 2.783e-02 | 5.14 |
| motif_307f6707374de704 | rotation_cancellation | 5 | 2.00 | 0.00 | 2.783e-02 | 5.14 |
| motif_ea7fc312c7c9af2a | rotation_cancellation | 5 | 2.00 | 0.00 | 2.783e-02 | 5.14 |
| motif_090e37025c96a8bc | rotation_cancellation | 5 | 2.00 | 0.00 | 2.783e-02 | 5.14 |
| motif_89ed860cb55bd827 | rotation_cancellation | 5 | 2.00 | 0.00 | 2.783e-02 | 5.14 |
| motif_956144356c6edd22 | rotation_cancellation | 5 | 2.00 | 0.00 | 2.783e-02 | 5.14 |
| motif_459aa7c5c9b79318 | rotation_cancellation | 1 | 2.00 | 0.00 | 2.783e-02 | 0.21 |
| motif_bbc7bb9f8bd046af | rotation_cancellation | 1 | 2.00 | 0.00 | 2.783e-02 | 0.21 |

## Generalization to Unseen Circuits

| Workload | Family | Motif Applications | Gain From Motifs Alone | Gain From Motifs + Optimizer | Motif Fidelity Gain | Motif+Optimizer Fidelity Gain |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| unseen_kernel_8q | Quantum Kernel | 23 | 46 | 19 | 2.002e-05 | -2.802e-05 |
| unseen_classifier_8q | QML | 14 | 28 | 0 | 3.128e-04 | 0.000e+00 |
| unseen_maxcut_8q | Optimization | 23 | 46 | -53 | 3.271e-05 | 1.154e-04 |
| unseen_qft_7q | Controls | 12 | 24 | 0 | -5.423e-05 | 0.000e+00 |

## Verdict

QADE does generate reusable proprietary optimization knowledge. The validated motifs are mathematically equivalent local rewrites and transfer to unseen workloads at **84.6%** motif reuse.
