# Phase 9-10 Gap Analysis

Fecha de análisis: 2026-05-31

Objetivo: determinar qué partes de las Fases 9.0, 9A, 9B, 9C, 10A, 10B y 10C ya existen parcial o totalmente para evitar duplicidades antes de implementar.

## Resumen Ejecutivo

La solicitud adjunta define nuevas fases para el dominio `physics/`. No debe confundirse con las fases térmicas `T9` y `T10` del dominio `satellite/`, que ya existen como `satellite/thermal/multi_node_thermal_network.py` y `satellite/thermal/orbital_environment.py`.

El repositorio ya contiene una parte importante de la infraestructura necesaria para Fase 9.0 y varias auditorías útiles para Fase 9A. Sin embargo, no existen los módulos finales pedidos con esos nombres (`physics/bias_detector.py`, `physics/physics_sanity_engine.py`, `physics/real_data_ingestor.py`, `physics/domain_adaptation.py`, `physics/expert_validation.py`) ni una clase base común `ScientificModule`.

Recomendación global:

- Refactorizar y envolver componentes existentes antes de crear lógica nueva.
- Crear módulos nuevos solo como fachadas/coordinadores cuando no exista una clase equivalente.
- Evitar duplicar la convención `T9/T10` del dominio `satellite`; documentar que esas fases ya pertenecen al stack térmico.

## Convenciones Ya Existentes Que Hay Que Respetar

| Área | Archivos existentes | Implicación |
|---|---|---|
| Artifacts y sesiones | `physics/core/io/artifact_manager.py`, `physics/core/io/session_exporter.py` | No crear otro gestor de rutas desde cero; extender o envolver. |
| Configuración YAML | `physics/config.yaml`, `physics/neurosymbolic/config.py` | `ConfigManager` debe reutilizar este loader. |
| Registro de experimentos | `physics/experiment_versioning.py`, `physics/core/evaluator_db.py` | `ExperimentRegistry` debe envolver o adaptar `ExperimentTracker`, no crear una segunda semántica incompatible. |
| Reportes | `physics/knowledge_graph.py`, `physics/core/autonomous/autonomous_scientist.py`, `physics/benchmark_scientific_system.py`, `physics/qg_autonomous_discovery.py` | Centralizar generación en `ReportManager`, pero reutilizando patrones existentes. |
| Modelos | `physics/models/*.pth`, `physics/models/ptbxl/*.pth`, `physics/artifacts/*.pth` | Crear índice/registro, no mover checkpoints. |
| Auditorías de sesgo/leakage | `physics/core/validation/strict_leakage_audit.py`, `dataset_bias_elimination_audit.py`, `causal_ablation_audit.py` | Fase 9A debe componer estas auditorías. |
| Datos reales ECG | `physics/core/empirical/mit_bih_bifurcated_audit.py`, `physionet_ecg_audit.py`, `physics/data/mitdb/*`, `physics/ucr_loader.py` | Fase 10A no debe reimplementar ingesta ECG/UCR; puede añadir NASA/NOAA/Materials como nuevos conectores. |
| CKA/reality gap | `physics/neurosymbolic/audit.py`, `physics/robustness_audit.py`, `physics/core/empirical/*` | Fase 10B debe reutilizar CKA existente y añadir Wasserstein/adaptation wrapper. |
| Scientific Guard | `physics/scientific_guard.py` | Fase 9C es una extensión directa, no un módulo nuevo. |

## Fase 9.0 - Capa de Orquestación Común

### Already Implemented

| Requisito | Estado | Archivos a reutilizar |
|---|---|---|
| `physics/core/__init__.py` | Existe | `physics/core/__init__.py` |
| Directorios `physics/core/` y subpaquetes | Existe con estructura avanzada | `physics/core/autonomous/`, `physics/core/io/`, `physics/core/neurosymbolic/`, `physics/core/schemas/`, `physics/core/validation/` |
| Loader de configuración YAML | Implementado fuera de `ConfigManager` | `physics/neurosymbolic/config.py`, `physics/config.yaml` |
| Exportación validada de sesiones | Implementada | `physics/core/io/session_exporter.py`, `physics/core/schemas/experiment_session.py` |
| Tracking SQLite de experimentos | Implementado con otro nombre/API | `physics/experiment_versioning.py` |
| Orquestador genérico de plugins | Implementado, pero no equivalente a `ScientificModule` | `physics/core/orchestrator.py` |

### Partially Implemented

| Requisito | Cobertura actual | Falta |
|---|---|---|
| `ArtifactManager` | `physics/core/io/artifact_manager.py` define `ARTIFACTS_DIR`, `LEGACY_ARTIFACTS_DIR` y `resolve_path()` | Clase `ArtifactManager`, métodos `save_json`, `load_json`, `save_csv`, `load_csv`, `save_markdown`, `list_artifacts`, `get_experiment_dir` |
| `ExperimentRegistry` | `ExperimentTracker` registra sistema, módulo, seed, hiperparámetros, resultados y estado | API exacta `register`, `update_status`, `list_by_module`, `list_by_status`, `get_statistics`; DB solicitada `physics/artifacts/experiment_registry.db` |
| `ReportManager` | Reportes se generan en varios módulos | Clase común con `generate_phase_report` y `append_to_changelog` |
| `ConfigManager` | `load_config()` existe y expande variables de entorno | API mutable `get`, `set`, `get_all`; persistencia segura en YAML |
| `ModelRegistry` | Existen modelos y checkpoints | Índice JSON `physics/models/model_registry.json`, metadata y búsqueda por nombre |
| `ScientificModule` | No existe como clase base, pero hay convenciones en pipelines | Clase abstracta común y contrato `run`, `log_result`, `get_status` |

### Missing

Estos archivos pedidos no existen:

- `physics/core/artifact_manager.py`
- `physics/core/experiment_registry.py`
- `physics/core/report_manager.py`
- `physics/core/config_manager.py`
- `physics/core/model_registry.py`
- `physics/core/base_module.py`

Nota: existe `physics/core/io/artifact_manager.py`, por lo que no conviene crear una implementación paralela incompatible.

### Refactor Instead Of Create

| Acción recomendada | Reutilizar |
|---|---|
| Convertir `physics/core/io/artifact_manager.py` en la implementación real de `ArtifactManager` y, si se necesita compatibilidad, crear `physics/core/artifact_manager.py` como wrapper/re-export. | `physics/core/io/artifact_manager.py`, `physics/core/io/session_exporter.py` |
| Implementar `ExperimentRegistry` como adaptador sobre `ExperimentTracker`, añadiendo solo los métodos faltantes. | `physics/experiment_versioning.py` |
| Implementar `ConfigManager` sobre `load_config()` y `physics/config.yaml`, evitando otro parser. | `physics/neurosymbolic/config.py`, `physics/config.yaml` |
| Crear `ReportManager` pequeño que centralice Markdown/changelog sin mover todos los reportes existentes. | `physics/knowledge_graph.py`, `physics/core/autonomous/autonomous_scientist.py`, `physics/benchmark_scientific_system.py`, `CHANGELOG.md` |
| Crear `ModelRegistry` como índice de los checkpoints existentes, no como nuevo storage. | `physics/models/`, `physics/models/ptbxl/`, `physics/artifacts/*.pth` |
| Crear `ScientificModule` y migrar gradualmente módulos nuevos; no refactorizar todo el repositorio de golpe. | Futuros `bias_detector.py`, `physics_sanity_engine.py`, `real_data_ingestor.py`, `domain_adaptation.py`, `expert_validation.py` |

## Fase 9A - Detector de Sesgos

### Already Implemented

| Requisito relacionado | Evidencia | Archivos a reutilizar |
|---|---|---|
| Auditoría de leakage y particiones independientes | Hay auditoría de zero-leakage, normalización independiente, detección de leakage y bias | `physics/core/validation/strict_leakage_audit.py` |
| Eliminación/verificación de sesgo de dataset | Auditoría de debiasing, grupos y verificación de sesgo | `physics/core/validation/dataset_bias_elimination_audit.py` |
| Ablación causal y splits sin leakage | Contiene particionamiento y pruebas causales | `physics/core/validation/causal_ablation_audit.py` |
| Importancias SHAP y MI como artefactos | Ya existen salidas generadas | `physics/artifacts/feature_importance_shap.json`, `physics/artifacts/feature_importance_mi.json`, `physics/feature_redundancy_analysis.py` |
| CKA y robustez bajo perturbación | Implementado en varias rutas | `physics/robustness_audit.py`, `physics/neurosymbolic/audit.py` |

### Partially Implemented

| Función pedida | Cobertura actual | Falta |
|---|---|---|
| `detect_data_leakage(X_train, X_test, threshold=0.95)` | Hay auditorías de leakage, pero no función genérica por similitud coseno train/test | Extraer función reutilizable y parametrizable |
| `detect_spurious_correlations(X, y, n_permutations=1000)` | Hay correlaciones, permutaciones y auditorías causales dispersas | Función Pearson + permutación + Bonferroni con API estable |
| `detect_overfitting(...)` | Hay benchmarks y métricas, pero no detector general con SHAP stability | Implementar gap train/val + estabilidad SHAP |
| `permutation_importance_test(...)` | Hay artefactos de importancia y modelos sklearn | Implementar wrapper con CI 95% |
| `run(pipeline_results_dir=None)` | Hay reportes JSON/MD, pero no clase `bias_detector.py` | Orquestar pruebas y emitir `physics/artifacts/bias_report.md` |

### Missing

- `physics/bias_detector.py`
- Clase que herede de `ScientificModule`
- `knockoff_filter(X, y, q=0.1)`
- Integración con `ArtifactManager`, `ReportManager`, `ExperimentRegistry`
- Reporte único `physics/artifacts/bias_report.md`

### Refactor Instead Of Create

No crear otra auditoría monolítica que duplique `strict_leakage_audit.py` y `dataset_bias_elimination_audit.py`.

Crear `physics/bias_detector.py` como fachada:

- Usar `physics/core/validation/strict_leakage_audit.py` para leakage.
- Usar `physics/core/validation/dataset_bias_elimination_audit.py` para bias.
- Usar `physics/core/validation/causal_ablation_audit.py` para pruebas causales.
- Usar `physics/feature_redundancy_analysis.py` y artefactos SHAP/MI para importancia.
- Añadir solo funciones faltantes genéricas: similitud coseno, Pearson/permutación/Bonferroni, knockoff, CI de permutation importance.

## Fase 9B - Motor de Consistencia Física

### Already Implemented

| Requisito relacionado | Evidencia | Archivos a reutilizar |
|---|---|---|
| Guardrails científicos contra sobreafirmaciones | Sanitización y validación de hipótesis | `physics/scientific_guard.py` |
| Comparación simbólica con ground truth | Evaluación de ecuaciones descubiertas contra ecuaciones reales | `physics/symbolic_discovery.py` |
| Ecuaciones ground truth de sistemas conocidos | Generadores y ecuaciones base | `physics/synthetic_systems.py` |
| Parseo SymPy seguro | `safe_parse_sympy` | `physics/symbolic_discovery.py` |
| Descubrimiento y validación de modelos QG con guard | Revisión de hipótesis y reportes | `physics/qg_autonomous_discovery.py`, `physics/scientific_guard.py` |

### Partially Implemented

| Función pedida | Cobertura actual | Falta |
|---|---|---|
| `check_mathematical_consistency(equation_str)` | SymPy parsing/evaluation existe en symbolic discovery | Detección explícita de singularidades, simplificación y estado estandarizado |
| `check_conservation_laws(equation_str, system_type)` | Hay ground truth para sistemas conocidos y tests científicos, pero no ley de conservación genérica | Tabla de reglas por sistema |
| `validate_hypothesis(hypothesis_dict)` | `validate_hypothesis_structure()` existe | Scoring físico 0-1 y unión de checks físicos |
| Cache por hash | No existe para sanity engine, pero hay patrones de DB/artefactos | Implementar cache JSON/SQLite |

### Missing

- `physics/physics_sanity_engine.py`
- `check_dimensional_consistency(equation_str, variable_units)`
- `check_boundedness(equation_str, variable_ranges, n_samples=100)`
- Cache interna de ecuaciones validadas por hash
- `physics/artifacts/sanity_log.json`
- `physics/artifacts/sanity_report.md`

### Refactor Instead Of Create

Crear `physics/physics_sanity_engine.py`, pero reutilizar:

- `physics/symbolic_discovery.py` para `safe_parse_sympy`, ground truth y evaluación simbólica.
- `physics/synthetic_systems.py` para sistemas conocidos.
- `physics/scientific_guard.py` para validación estructural de hipótesis.
- `physics/core/io/artifact_manager.py` para guardar `sanity_log.json`.
- `physics/knowledge_graph.py` si se auditan hipótesis desde Neo4j, con fallback si está offline.

## Fase 9C - Scientific Guard v2

### Already Implemented

| Requisito | Estado | Archivos a reutilizar |
|---|---|---|
| `sanitize_hypothesis` | Implementado | `physics/scientific_guard.py` |
| `validate_hypothesis_structure` | Implementado | `physics/scientific_guard.py` |
| `reality_check` | Implementado | `physics/scientific_guard.py` |
| Lista de frases bloqueadas | Implementada como constante | `physics/scientific_guard.py` |

### Partially Implemented

| Requisito v2 | Cobertura actual | Falta |
|---|---|---|
| Frases bloqueadas desde config | Lista existe, pero hardcodeada | Añadir sección `scientific_guard.blocked_phrases` en `physics/config.yaml` y loader |
| Etiquetado de reportes | `reality_check()` escanea reportes | `tag_conclusions(report_path)` que reescriba/etiquete afirmaciones |
| Claim report agregado | No existe | `generate_claim_report(report_paths)` |

### Missing

- `assign_claim_level(conclusion_text, supporting_evidence)`
- `tag_conclusions(report_path)`
- `generate_claim_report(report_paths)`
- `physics/artifacts/claim_level_report.md`
- Configuración `scientific_guard.blocked_phrases` en `physics/config.yaml`

### Refactor Instead Of Create

No crear `scientific_guard_v2.py`. Modificar `physics/scientific_guard.py` conservando API actual.

Archivos a reutilizar:

- `physics/scientific_guard.py`
- `physics/config.yaml`
- `physics/neurosymbolic/config.py`
- `physics/core/io/artifact_manager.py`
- Reportes existentes en `physics/artifacts/*.md` y `dashboard/public/artifacts/discoveries/*.json`

## Fase 10A - Integración de Datasets Reales

### Already Implemented

| Fuente/capacidad | Evidencia | Archivos a reutilizar |
|---|---|---|
| MIT-BIH / PhysioNet ECG | Downloader/cache y procesamiento AAMI | `physics/core/empirical/mit_bih_bifurcated_audit.py`, `physics/data/mitdb/*` |
| ECG sintético/realista | Generador biológico y auditoría empírica | `physics/core/empirical/physionet_ecg_audit.py` |
| UCR datasets | Descarga/carga/extracción EV3 | `physics/ucr_loader.py`, `physics/data/ucr/*` |
| Feature extractor EV3 | Embedding vector común | `physics/core/autonomous/latent_snapshot_exporter.py` |

### Partially Implemented

| Requisito pedido | Cobertura actual | Falta |
|---|---|---|
| Catalogación de datasets reales | `datasets/README.md` cataloga datasets del proyecto | Generador automático `physics/data/real_data_catalog.md` solo con descargas exitosas |
| Conversión a formato EV3 | Existe para UCR/ECG | API general `convert_to_pipeline_format(dataset_name, raw_data)` |
| TUH EEG opcional | No existe TUH, pero hay patrón de dependencia opcional en MIT-BIH | Implementar skip no bloqueante |

### Missing

- `physics/real_data_ingestor.py`
- `download_kepler_data(kepid)`
- `download_noaa_data(dataset, start, end)`
- `download_materials_data(material_id)`
- `generate_real_data_catalog()`
- `physics/data/real/`
- Ingesta NASA Kepler / MAST
- Ingesta NOAA GHCN-D y Mauna Loa
- Ingesta Materials Project
- Gestión de API key para Materials Project

### Refactor Instead Of Create

Crear `physics/real_data_ingestor.py`, pero reutilizar:

- `physics/ucr_loader.py` para patrón download/load/cache.
- `physics/core/empirical/mit_bih_bifurcated_audit.py` para patrón de descarga robusta y cache local.
- `physics/core/autonomous/latent_snapshot_exporter.py` para EV3.
- `datasets/README.md` como fuente de estilo para catálogo.
- `physics/config.yaml` para rutas y claves opcionales.

No reimplementar ECG/UCR dentro de 10A; registrarlos como fuentes ya existentes.

## Fase 10B - Domain Adaptation

### Already Implemented

| Requisito relacionado | Evidencia | Archivos a reutilizar |
|---|---|---|
| CKA | Implementado en varias rutas | `physics/neurosymbolic/audit.py`, `physics/robustness_audit.py`, `physics/core/empirical/mit_bih_bifurcated_audit.py` |
| Medición de transferencia sintético-clínico | Auditorías ECG/biophysical | `physics/core/empirical/mit_bih_bifurcated_audit.py`, `physics/core/empirical/causal_continuity_audit.py` |
| Robustez y OOD | Resultados y auditorías | `physics/robustness_audit.py`, `physics/core/validation/raw_embedding_robustness_closure_audit.py`, `physics/results/phase8e/*` |
| Modelos base / fine-tuned | Checkpoints existentes | `physics/models/*_base.pth`, `physics/models/*_ft.pth`, `physics/models/ptbxl/*` |

### Partially Implemented

| Función pedida | Cobertura actual | Falta |
|---|---|---|
| `measure_reality_gap(...)` | CKA existe; comparativas sintético/real existen | Wasserstein 1D y API común |
| `train_domain_adaptation(source, target, method="transfer")` | Existen modelos base/ft y scripts de entrenamiento ECG | Wrapper formal con métodos `"transfer"`, `"joint"`, `"calibrate"` |
| `validate_transfer_performance(...)` | Métricas de transferencia existen en reportes/scripts | Métrica estándar de porcentaje retenido |
| Hito `>80%` en 3 dominios | No verificable con los tres dominios nuevos | Requiere 10A completo |

### Missing

- `physics/domain_adaptation.py`
- Reporte `physics/artifacts/domain_adaptation_report.md`
- Integración con datasets reales de 10A
- Métodos formales `"transfer"`, `"joint"`, `"calibrate"` bajo una sola API
- Validación del hito de 3 dominios reales

### Refactor Instead Of Create

Crear `physics/domain_adaptation.py` como módulo coordinador.

Reutilizar:

- `physics/neurosymbolic/audit.py` para CKA.
- `physics/robustness_audit.py` para degradación y CKA bajo ruido.
- `physics/core/empirical/mit_bih_bifurcated_audit.py` para sintético/biophysical/clinical.
- `physics/core/empirical/causal_continuity_audit.py` para continuidad causal.
- `physics/train_ecg_models.py` y `physics/train_all_architectures_ptbxl.py` para entrenamiento existente.
- `physics/models/*` para base/fine-tuned checkpoints.

## Fase 10C - Validación Externa con Expertos

### Already Implemented

| Requisito relacionado | Evidencia | Archivos a reutilizar |
|---|---|---|
| Papers locales | Existen manuscritos LaTeX/PDF/MD | `papers/system/*`, `physics/papers/*`, `papers/thermal/`, `papers/qg/` |
| Conversión de feedback a hipótesis puede apoyarse en KG | Knowledge graph e hipótesis ya existen | `physics/knowledge_graph.py`, `physics/core/autonomous/autonomous_scientist.py` |
| Reportes de investigación | Generadores de reportes científicos existen | `physics/core/autonomous/research_reporter.py`, `physics/auto_paper_generator.py` |

### Partially Implemented

| Función pedida | Cobertura actual | Falta |
|---|---|---|
| `prepare_paper_for_review(paper_path, anonymize=True)` | Hay papers y generadores, pero no anonimización | Implementar limpieza de autor/metadatos |
| `convert_feedback_to_hypotheses(feedback_points)` | KG e hipótesis existen | Parser + inserción formal |
| `track_review_cycle(...)` | Hay reportes y DBs, pero no ciclo de revisión | Log dedicado `review_cycle_log.md` |

### Missing

- `physics/expert_validation.py`
- `generate_reviewer_invitation(reviewer_email, paper_title)`
- `parse_reviewer_feedback(feedback_text)`
- Flujo de revisión externo completo
- `review_cycle_log.md`
- Plantillas de email/invitación
- Almacenamiento formal de acciones tomadas por versión de paper

### Refactor Instead Of Create

Crear `physics/expert_validation.py` como módulo nuevo, pero reutilizar:

- `papers/system/representation_aware_system_identification.tex`
- `physics/papers/system_paper.md`
- `physics/auto_paper_generator.py`
- `physics/core/autonomous/research_reporter.py`
- `physics/knowledge_graph.py`
- `physics/core/autonomous/hypothesis_engine.py` si se normalizan críticas como hipótesis.

No crear un segundo sistema de papers; operar sobre `papers/` y `physics/papers/`.

## Colisión De Nombres: Fase 9/10 vs T9/T10

El repositorio ya usa `T9` y `T10` para el dominio `satellite`:

| Fase existente | Estado | Archivos |
|---|---|---|
| `T9` - Multi-node thermal network | Implementado | `satellite/thermal/multi_node_thermal_network.py`, `satellite/tests/test_satellite_twin.py`, `satellite/run_thermal_pipeline.py` |
| `T10` - Orbital environment | Implementado | `satellite/thermal/orbital_environment.py`, `satellite/ARCHITECTURE.md`, `satellite/ROADMAP.md` |

No reutilizar esos nombres para los nuevos módulos `physics/` salvo que el documento hable explícitamente de `Phase 9.0`, `9A`, `9B`, `9C`, `10A`, `10B`, `10C`.

## Matriz Final De Decisión

| Subfase | Already implemented | Partially implemented | Missing | Refactor instead of create |
|---|---|---|---|---|
| 9.0 Common orchestration | `physics/core/`, config loader, session exporter, experiment tracker | Artifact manager, experiment registry, report manager, config manager, model registry | `base_module.py` and exact manager classes | Extend `core/io/artifact_manager.py`; wrap `experiment_versioning.py`; use `neurosymbolic/config.py` |
| 9A Bias detector | Leakage/bias/causal audit scripts | Generic leakage/spurious/overfit APIs | `bias_detector.py`, knockoff filter, unified report | Compose `core/validation/*` and `feature_redundancy_analysis.py` |
| 9B Physics sanity engine | Scientific guard, symbolic parsing/evaluation, ground truth systems | Mathematical/hypothesis validation pieces | `physics_sanity_engine.py`, dimensional/boundedness/cache/report | Reuse `symbolic_discovery.py`, `synthetic_systems.py`, `scientific_guard.py` |
| 9C Scientific Guard v2 | v1 guard functions | report scanning | claim levels, report tagging, config-loaded blocked phrases | Modify `scientific_guard.py`; do not create v2 file |
| 10A Real data ingestor | MIT-BIH, UCR, ECG ingestion patterns | catalog and EV3 conversion patterns | Kepler, NOAA, Materials, TUH optional, `real_data_ingestor.py` | Reuse `ucr_loader.py`, empirical audits, EV3 extractor |
| 10B Domain adaptation | CKA, ECG transfer audits, base/ft model artifacts | reality-gap pieces and transfer metrics | `domain_adaptation.py`, Wasserstein wrapper, method API, report | Reuse `neurosymbolic/audit.py`, empirical audits, train scripts |
| 10C Expert validation | Papers, KG, report generators | feedback-to-hypothesis infrastructure | `expert_validation.py`, anonymization, invitation, parser, review log | Reuse `papers/`, `auto_paper_generator.py`, `knowledge_graph.py` |

## Implementación Recomendada En Orden

1. Crear primero `physics/core/base_module.py`, `config_manager.py`, `report_manager.py`, `model_registry.py`, y extender `physics/core/io/artifact_manager.py`.
2. Crear `physics/core/experiment_registry.py` como adaptador de `physics/experiment_versioning.py`.
3. Extender `physics/scientific_guard.py` a v2, cargando frases desde `physics/config.yaml`.
4. Implementar `physics/bias_detector.py` como fachada de auditorías existentes.
5. Implementar `physics/physics_sanity_engine.py` reutilizando `symbolic_discovery.py`.
6. Implementar `physics/real_data_ingestor.py` solo para fuentes no existentes: Kepler, NOAA, Materials Project y TUH opcional.
7. Implementar `physics/domain_adaptation.py` sobre datasets reales ya descargados.
8. Implementar `physics/expert_validation.py` como sistema de workflow/documentación, no como sistema de papers nuevo.

## Archivos Que No Deben Duplicarse

- `physics/core/io/artifact_manager.py`
- `physics/core/io/session_exporter.py`
- `physics/experiment_versioning.py`
- `physics/neurosymbolic/config.py`
- `physics/scientific_guard.py`
- `physics/symbolic_discovery.py`
- `physics/synthetic_systems.py`
- `physics/ucr_loader.py`
- `physics/core/autonomous/latent_snapshot_exporter.py`
- `physics/core/validation/strict_leakage_audit.py`
- `physics/core/validation/dataset_bias_elimination_audit.py`
- `physics/core/validation/causal_ablation_audit.py`
- `physics/core/empirical/mit_bih_bifurcated_audit.py`
- `physics/core/empirical/physionet_ecg_audit.py`
- `physics/core/empirical/causal_continuity_audit.py`
- `physics/neurosymbolic/audit.py`
- `physics/robustness_audit.py`
- `physics/knowledge_graph.py`
- `physics/auto_paper_generator.py`
- `physics/core/autonomous/research_reporter.py`
