# QADE IP Asset Register

Generated: 2026-06-06

| Asset | Description | Origin | Reusability | Commercial Value | Patent Potential | Licensing Potential |
| --- | --- | --- | --- | --- | --- | --- |
| Hardware cost model | Uses backend T1/T2, gate length, gate error, readout error, duration, swaps and log-fidelity scoring | Phase III | High | High | Medium | High |
| Coherence-aware SABRE routing | Extends routing cost with duration and coherence-loss terms | Phase III | High | High | Medium | High |
| Fidelity-aware placement | Maps active logical qubits to high-quality physical qubits using T1/T2/readout/gate-error scores | Phase III | High | High | Medium | High |
| Motif discovery engine | Extracts local graph/gate transformations from original and optimized circuits | Phase V | High | High | High | High |
| Motif validator | Unit-matrix/equivalence validation with high-fidelity acceptance threshold | Phase V | High | High | Medium | High |
| Motif knowledge graph | Stores motif-to-family/topology/hardware/gain/confidence relationships | Phase V | High | High | High | High |
| Motif ranking model | Scores motifs by frequency, gate saving, fidelity improvement and hardware relevance | Phase V | High | Medium-High | Medium | High |
| Motif reuse engine | Reapplies learned rewrites to unseen circuits before normal optimization | Phase V | High | High | High | High |
| Generalization benchmark | Measures transfer from seen to unseen workloads | Phase V | Medium-High | High | Medium | High |
| Economic motif profiling | Converts motifs into hardware savings, shots saved, and execution cost savings | Phase VI | High | High | Medium | High |
| IP portfolio valuation | Estimates replacement cost, research-equivalent cost, IP value, and licensing value | Phase VI | Medium | High | Low-Medium | High |
| Knowledge flywheel model | Models motif accumulation, value growth, and network effects across workloads/customers | Phase VII | Medium | High | Low-Medium | Medium-High |
| Competitive gap model | Estimates competitor catch-up cost/time | Phase VII | Medium | Medium-High | Low | Medium |
| QADE benchmark corpus | Phase III-VII CSV/report suite covering compilers, workloads, hardware, economics, and moat | Phase III-VII | High | High | Low | Medium-High |
| Compiler integration adapters | Qiskit, PyZX, TKET, BQSKit, Cirq adapters and fallbacks | QADE integration | High | Medium | Low | Medium |

## Summary

QADE strongest IP is not a single gate rewrite. It is the validated loop that discovers reusable motifs, proves equivalence, measures hardware benefit, stores knowledge, transfers it to unseen workloads, and assigns economic value.

## Expanded IP Register Notes

### IP Priority Ranking

| Priority | Asset | Reason | Protection Urgency |
| --- | --- | --- | --- |
| 1 | Validated motif database | Most defensible knowledge asset and licensing candidate | High |
| 2 | Motif discovery + validation pipeline | Core method that generates future IP | High |
| 3 | Hardware-aware cost model | Differentiates QADE from gate-count-only optimization | Medium-High |
| 4 | Motif transferability and failure statistics | Hard to reproduce without usage history | High |
| 5 | Economic valuation engine | Supports commercial licensing and investor story | Medium |
| 6 | Knowledge flywheel model | Strategic positioning asset | Medium |

### Patent Versus Trade Secret Guidance

Patent candidates should focus on pipeline combinations that are non-obvious and technically specific. Trade secret protection should cover motif contents, ranking weights, transfer scores, customer-derived motifs, and failure boundaries. Copyright protects the source code and reports but does not protect the underlying optimization idea.

### Contributor and Employee Readiness

Before adding external contributors, contractors, employees, or partners, QADE needs a written IP assignment and confidentiality policy. Without this, future ownership of motifs, code, and benchmark outputs may be harder to prove.
