# QADE Phase III Reproducibility Guide

Run the complete Phase III benchmark suite with:

```bash
python run_all_benchmarks.py
```

For a smoke run during development:

```bash
$env:QADE_PHASE3_QUICK = "1"
python run_all_benchmarks.py
```

Outputs:

* `benchmarks/results/PHASE3_HARDWARE_AWARE_RESULTS.csv`
* `benchmarks/results/PHASE3_ROUTING_PLACEMENT_ABLATION.csv`
* `benchmarks/reports/PHASE3_HARDWARE_AWARE_REPORT.md`
* `benchmarks/reports/PHASE3_INVESTOR_SUMMARY.md`
