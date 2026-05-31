# Meta-Learning Expansion Report

## Metrics

| Metric | Value |
|---|---|
| `expanded_rows` | 119 |
| `domains` | {"lorenz": 80, "physics": 12, "physical_lab": 10, "cross_domain": 4, "hpc": 4, "distributed_execution": 2, "multi": 2, "scalar_field": 1, "Lorenz_to_Climate": 1, "ECG_to_EEG": 1, "Fluids_to_Materials": 1, "QG_to_Materials": 1} |
| `methods` | {"MultiAgentSystem": 69, "PhysicalLabInterface": 11, "multi_agent_debate": 10, "CrossDomainTransfer": 5, "distributed_execution": 4, "cross_domain_transfer": 4, "DistributedExecution": 3, "MetaLearningEngine": 3, "FrontierDiscovery": 3, "BiasDetector": 1, "DomainAdaptation": 1, "PhysicsSanityEngine": 1, "ExpertValidation": 1, "RealDataIngestor": 1, "ScientificMemoryAdvanced": 1, "TheoryAutowriter": 1} |
| `mae` | 0.652977348661823 |
| `rmse` | 1.7686212065206255 |
| `r2` | 0.5379605314209532 |
| `cv_score_mean` | -0.3033231600165491 |
| `cv_score_std` | 2.239605992447133 |
| `model_path` | C:\Users\Alvaro\Desktop\ia-matematica-github\physics\models\meta_prior_learner.pkl |
| `expanded_cache` | C:\Users\Alvaro\Desktop\ia-matematica-github\physics\artifacts\meta_history_expanded.csv |

## Notes

- The existing MetaLearningEngine was retrained using the expanded historical table.
