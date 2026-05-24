# Autonomous Neurosymbolic Scientist for Dynamical Systems and Clinical ECG

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20366363.svg)](https://doi.org/10.5281/zenodo.20366363)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-Neural%20ODEs%20%7C%20ResNet--1D-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![DeepXDE](https://img.shields.io/badge/DeepXDE-PINNs-0f766e?style=flat-square)](https://deepxde.readthedocs.io/)
[![PySR](https://img.shields.io/badge/PySR-Symbolic%20Regression-7c3aed?style=flat-square)](https://github.com/MilesCranmer/PySR)
[![Next.js](https://img.shields.io/badge/Next.js-16.2.6-000000?style=flat-square&logo=nextdotjs&logoColor=white)](dashboard/package.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

This repository implements an **Autonomous Neurosymbolic Scientist**: a closed-loop AI4Science system that proposes falsifiable hypotheses, designs computational experiments, executes them in a sandbox, audits the resulting evidence, and writes persistent scientific memory. It extends the Phase 1 Zenodo preprint on cross-domain transfer in ECG from a static epistemological audit into an autonomous discovery engine for nonlinear dynamics, neural differential equations, symbolic law recovery, and deep representational validation.

Phase 1 established the central empirical paradox:

$$
D_{emb} = 1 - CKA(E_A, E_C) \gg D_{attr} = 1 - \rho(\bar{C}_A, \bar{C}_C)
$$

Predictive transfer from synthetic chaotic attractors to clinical ECG can survive even when geometric representational alignment collapses. Phase 2 turns that finding into an executable research program: continuous latent dynamics are learned, candidate physical laws are rediscovered, neural baselines are audited, and LLM-driven agents decide which hypotheses deserve the next experiment.

---

## Core Architecture

### 1. Autonomous Hypothesis-to-Evidence Loop

`autonomous_scientist.py` and `llm_reasoner.py` implement the scientific control plane. The agent builds context from prior hypotheses, available dynamical systems, analytic methods, and experiment history; asks an LLM to generate a quantitative falsifiable hypothesis; requests executable Python for a test; runs the code through a sandbox; interprets the result; computes epistemic gain from prior-posterior entropy, novelty, and utility; and persists the outcome to Neo4j or a local SQLite fallback (`scientific_kb.db`).

The loop is intentionally falsification-oriented. Each experiment must expose a metric and a failure criterion, and failed code enters an LLM self-correction loop before being discarded.

### 2. Deep Clinical Baseline and Representation Audit

`baseline_deep_ecg.py` implements a ResNet-18-style 1D convolutional baseline for raw MIT-BIH ECG segments under strict AAMI inter-patient partitioning. It trains on 360-sample windows centered on annotated beats, exports weights to `artifacts/resnet1d_ecg.pt`, and writes prediction and metric artifacts.

`deep_representation_audit.py` then removes the classifier head, extracts 512-dimensional deep features from the adaptive average pooling layer, and compares representational deformation across:

- Domain A: synthetic chaotic signals.
- Domain B: composite biophysical cardiac simulations.
- Domain C: clinical MIT-BIH ECG.

The audit computes linear CKA for deep features and compares it directly against the 8D EV3 embedding space, testing whether the Phase 1 asymmetry persists beyond Random Forests and handcrafted invariants.

### 3. Neural Differential Equations, PINNs, and Operator Learning

`neural_ode_module.py` learns continuous-time vector fields with `torchdiffeq`. It fits an MLP derivative function \(f_\theta(t, x)\), integrates trajectories with RK4, forecasts unseen horizons, and saves trained Neural ODE weights under `artifacts/`.

`pinn_module.py` uses DeepXDE PINNs for forward and inverse ODE problems. It supports Lorenz, Rossler, Duffing, and Van der Pol residuals, combines Adam with L-BFGS refinement, and can discover physical parameters such as `sigma`, `rho`, `beta`, `a`, `b`, and `c` from observed trajectories.

`operator_learning.py` adds a DeepONet layer: a branch-trunk neural operator that maps sampled parameters or input functions to solution trajectories. This allows the system to learn families of ODE solution operators rather than isolated trajectories.

### 4. Symbolic Law Discovery

`symbolic_discovery.py` closes the neurosymbolic loop. It supports:

- SINDy-style sparse identification of nonlinear dynamics.
- PySR evolutionary symbolic regression.
- Deterministic fallback recovery when Julia/PySR is unavailable.
- SymPy-based parsing, simplification, and comparison to ground-truth equations.
- Physics-informed penalties for expected and forbidden terms.

The benchmark layer evaluates discovered equations on Lorenz, Rossler, Duffing, Van der Pol, and logistic systems, exporting structured reports such as `artifacts/discovery_lorenz_sindy.json` and `artifacts/discovery_benchmark_report.json`.

---

## Scientific Workflow

```text
Hypothesis generation
        |
        v
LLM experiment design  --->  sandbox execution  --->  result interpretation
        |                         |                         |
        v                         v                         v
Neural ODE / PINN          symbolic regression        epistemic gain
DeepONet operators         SINDy / PySR               posterior update
Deep ECG CKA audit         physics penalties          knowledge graph
        |                         |                         |
        +-------------------------+-------------------------+
                                  |
                                  v
                     artifacts/ + dashboard observability
```

The result is not a single model. It is a reproducible machine scientist for testing whether representations, dynamics, and symbolic laws remain stable under domain shift, noise, and clinical biophysical complexity.

---

## Quickstart

### 1. Python Environment

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1

pip install numpy pandas scipy scikit-learn sympy matplotlib wfdb torch torchdiffeq deepxde pysindy json5 tenacity
```

Optional components:

```bash
pip install pysr openai anthropic
```

If `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is absent, `LLMReasoner` falls back to deterministic mock simulation mode so the autonomous loop remains testable.

### 2. Run the Autonomous Sweep

```bash
python run_autonomous_sweep.py
```

This launches the automated noise-sweep pipeline, runs `run_pipeline.py` over multiple perturbation levels, analyzes geometric drift, evaluates hypotheses, and exports a consolidated report to:

```text
artifacts/discoveries/noise_robustness_report.json
```

### 3. Run the Open-Ended Autonomous Scientist

```bash
python -c "from autonomous_scientist import AutonomousScientist; s=AutonomousScientist(llm_provider='openai', use_docker=False); s.auto_mode=True; s.run_discovery_cycle(domain='nonlinear dynamical systems and ECG transfer', goal='discover falsifiable laws governing representational collapse under noise', max_iterations=3)"
```

Outputs are written to:

```text
artifacts/discovery_report.md
artifacts/autonomous_session.json
scientific_kb.db
```

### 4. Train and Audit the Deep ECG Baseline

```bash
python baseline_deep_ecg.py
python deep_representation_audit.py
```

Expected outputs include:

```text
artifacts/resnet1d_ecg.pt
artifacts/resnet_metrics.json
artifacts/resnet_predictions.json
artifacts/deep_cka_comparison.json
```

### 5. Run Symbolic and Differential Discovery Modules

```bash
python -c "from symbolic_discovery import run_full_discovery_benchmark; from neural_ode_module import train_neural_ode_on_system; run_full_discovery_benchmark(); train_neural_ode_on_system('duffing', n_timesteps=1000, epochs=300)"
```

### 6. Launch the Scientific Dashboard

```bash
cd dashboard
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

The dashboard reads exported artifacts for experiment replay, representation drift, massive sweeps, scientific logs, hypotheses, benchmark panels, and multilingual research views.

---

## Repository Map

```text
.
|-- autonomous_scientist.py          # Closed-loop autonomous discovery engine
|-- llm_reasoner.py                  # LLM JSON reasoning, retry, mock fallback
|-- sandbox_executor.py              # Isolated execution of generated experiments
|-- symbolic_discovery.py            # SINDy, PySR, SymPy evaluation, physics penalties
|-- operator_learning.py             # DeepONet solution-operator learning
|-- pinn_module.py                   # Forward/inverse Physics-Informed Neural Networks
|-- neural_ode_module.py             # Continuous-time Neural ODE training and forecasting
|-- baseline_deep_ecg.py             # ResNet-1D clinical ECG baseline
|-- deep_representation_audit.py     # Deep CKA vs EV3 representation audit
|-- run_autonomous_sweep.py          # Autonomous robustness sweep entry point
|-- run_pipeline.py                  # Experiment/session pipeline backend
|-- core/
|   |-- autonomous/                  # Sweep scheduler, analyzer, hypothesis evaluator
|   |-- empirical/                   # MIT-BIH and causal continuity audits
|   |-- io/                          # Artifact/session export utilities
|   `-- validation/                  # Leakage, robustness, reproducibility, certification
|-- dashboard/                       # Next.js scientific observability interface
|-- artifacts/                       # Reports, trained models, predictions, discovery outputs
|-- data/                            # Local UCR and MIT-BIH data assets
|-- figures/                         # Phase 1 scientific figures
`-- scientific_kb.db                 # Local scientific memory fallback
```

---

## Phase 1 Reference Result

The Phase 1 preprint is archived on Zenodo:

https://doi.org/10.5281/zenodo.20366363

It reports that a compact amplitude-invariant EV3 representation can support clinical ECG transfer while failing to preserve strong geometric alignment:

- MIT-BIH AAMI clinical transfer with Random Forest EV3.
- Deep representational replication with ResNet-1D CKA.
- \(D_{emb} \approx 0.982\) for synthetic-to-clinical representational divergence.
- \(D_{attr} \approx 0.763\) for attributional reordering.
- The key conclusion: predictive transfer does not imply representational invariance.

---

## Citation

If you use this repository or the Phase 1 audit, please cite:

```bibtex
@misc{lopezalmeida2026predictive,
  title        = {Predictive Transfer Without Strong Representational Alignment from Synthetic Chaotic Attractors to Clinical ECG},
  author       = {Lopez Almeida, Alvaro},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.20366363},
  url          = {https://doi.org/10.5281/zenodo.20366363},
  note         = {Preprint}
}
```

---

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
