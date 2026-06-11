# QADE Phase III Investor Summary

QADE Phase III moves the compiler from gate-count optimization to hardware-aware optimization using backend T1/T2, gate duration, gate error, readout error, physical qubit quality, and SWAP overhead.

## Headline Metrics

* Win rate vs Qiskit L3 by estimated fidelity: **28.0%**.
* Mean estimated-fidelity improvement vs Qiskit L3 on non-underflow baselines: **10.20%**.
* Median log10 fidelity ratio vs Qiskit L3 across all matched cases: **0.00**.
* Impact of coherence-aware SABRE vs baseline SABRE in ablation: **-0.62%** relative fidelity change.
* Mean compile time for QADE Phase III: **3540.1 ms**.

## Trade-off

The new pipeline may spend additional compile time on calibrated placement and coherence-aware SWAP scoring, but it directly targets the Phase II failure mode where gate savings were erased by longer critical paths and T1/T2 decay.
