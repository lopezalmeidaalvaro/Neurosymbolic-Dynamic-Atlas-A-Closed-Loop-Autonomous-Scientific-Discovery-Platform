import os
import sys
import json
import numpy as np
from scipy.stats import spearmanr

# Ensure UTF-8 output encoding for Windows terminal
import io
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SNAPSHOTS_FILE = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "embeddings", "manifold_snapshots.json")
REPORT_DIR = os.path.join(ROOT_DIR, "dashboard", "public", "artifacts", "discoveries")
REPORT_FILE = os.path.join(REPORT_DIR, "reproducibility_report.json")

def main():
    print("=" * 60)
    print("🔬 RUNNING SCIENTIFIC STATISTICAL VALIDATION PIPELINE")
    print("=" * 60)
    
    if not os.path.exists(SNAPSHOTS_FILE):
        print(f"❌ Snapshots file not found at {SNAPSHOTS_FILE}. Run latent_snapshot_exporter.py first.")
        sys.exit(1)
        
    with open(SNAPSHOTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    systems_data = data.get("systems", [])
    
    # Task 1: POINT DENSITY
    point_counts = []
    point_counts_all = []
    
    for sys_entry in systems_data:
        sys_name = sys_entry["system"]
        for snap in sys_entry["snapshots"]:
            pc = snap["quantitative_metrics"]["point_count"]
            point_counts_all.append(pc)
            if sys_name != "logistic_sweep":
                point_counts.append(pc)
                
    if not point_counts:
        print("❌ No trajectory snapshots found for density check.")
        sys.exit(1)
        
    min_pc = min(point_counts)
    mean_pc = float(np.mean(point_counts))
    max_pc = max(point_counts)
    
    print("POINT DENSITY (Excluding logistic_sweep):")
    print(f"  min(point_count)  = {min_pc}")
    print(f"  mean(point_count) = {mean_pc:.2f}")
    print(f"  max(point_count)  = {max_pc}")
    print("POINT DENSITY (All systems):")
    print(f"  min(point_count)  = {min(point_counts_all)}")
    print(f"  mean(point_count) = {np.mean(point_counts_all):.2f}")
    print(f"  max(point_count)  = {max(point_counts_all)}")
    print("-" * 60)
    
    # Task 5: Reproducibility Analysis
    required_min_points = 320
    
    # Primary & Secondary Metrics
    primary_metrics = ["covariance_determinant", "nearest_neighbor_distance_mean", "nearest_neighbor_distance_std"]
    secondary_metrics = ["cluster_count"]
    all_metrics = primary_metrics + secondary_metrics
    
    reproducibility_results = {}
    
    validation_passed = True
    fail_reasons = []
    
    # Density failure check
    if min_pc < required_min_points:
        validation_passed = False
        fail_reasons.append(f"min(point_count) ({min_pc}) is less than required_min_points ({required_min_points})")
        
    # Process each system
    systems_checked = []
    
    for sys_entry in systems_data:
        sys_name = sys_entry["system"]
        snapshots = sys_entry["snapshots"]
        
        # Group by noise level
        noise_groups = {}
        for snap in snapshots:
            noise = snap["noise"]
            if noise not in noise_groups:
                noise_groups[noise] = []
            noise_groups[noise].append(snap)
            
        # We need a system that has multiple noise levels and multiple seeds per noise
        unique_noises = sorted(list(noise_groups.keys()))
        if len(unique_noises) < 3:
            # Baseline or single-run systems
            continue
            
        # Check if we have multiple seeds (at least 2, preferably 3)
        max_seeds_per_noise = max(len(snaps) for snaps in noise_groups.values())
        if max_seeds_per_noise < 2:
            continue
            
        print(f"Auditing reproducibility for sweep system: {sys_name} ({len(unique_noises)} noise levels, max {max_seeds_per_noise} seeds)")
        systems_checked.append(sys_name)
        reproducibility_results[sys_name] = {}
        
        # For each metric, compute Spearman and CV/CI
        system_failed = False
        system_reasons = []
        
        for metric in all_metrics:
            noise_levels = []
            metric_means = []
            cv_values = []
            ci95_widths = []
            
            for noise in unique_noises:
                snaps = noise_groups[noise]
                vals = [snap["quantitative_metrics"][metric] for snap in snaps]
                n = len(vals)
                
                mean_val = float(np.mean(vals))
                std_val = float(np.std(vals))
                
                # CI95 = 1.96 * (std / sqrt(n))
                ci95 = 1.96 * (std_val / np.sqrt(n)) if n > 0 else 0.0
                ci95_width = 2.0 * ci95
                
                # CV = std / (abs(mean) + 1e-8)
                cv = std_val / (abs(mean_val) + 1e-8)
                
                noise_levels.append(noise)
                metric_means.append(mean_val)
                cv_values.append(cv)
                ci95_widths.append(ci95_width)
                
            # Spearman correlation
            if len(noise_levels) > 1:
                rho, pvalue = spearmanr(noise_levels, metric_means)
                if not np.isfinite(rho):
                    rho = 0.0
                if not np.isfinite(pvalue):
                    pvalue = 1.0
            else:
                rho, pvalue = 0.0, 1.0
                
            mean_cv = float(np.mean(cv_values))
            mean_ci95_width = float(np.mean(ci95_widths))
            
            # Save results
            reproducibility_results[sys_name][metric] = {
                "spearman_rho": float(rho),
                "spearman_pvalue": float(pvalue),
                "mean_cv": mean_cv,
                "mean_ci95_width": mean_ci95_width,
                "noise_means": {float(n_val): float(m_val) for n_val, m_val in zip(noise_levels, metric_means)},
                "noise_cvs": {float(n_val): float(cv_val) for n_val, cv_val in zip(noise_levels, cv_values)}
            }
            
        # Stop condition checks per system
        # Check if |rho| < 0.5 for all primary metrics
        # Check if pvalue >= 0.05 for all primary metrics
        # Check if CV > 0.5 for all primary metrics
        failed_rho_count = 0
        failed_pvalue_count = 0
        failed_cv_count = 0
        
        for metric in primary_metrics:
            m_res = reproducibility_results[sys_name][metric]
            if abs(m_res["spearman_rho"]) < 0.5:
                failed_rho_count += 1
            if m_res["spearman_pvalue"] >= 0.05:
                failed_pvalue_count += 1
            if m_res["mean_cv"] > 0.5:
                failed_cv_count += 1
                
        if failed_rho_count == len(primary_metrics):
            system_failed = True
            system_reasons.append(f"|rho| < 0.5 for all primary metrics (rho values: {[reproducibility_results[sys_name][m]['spearman_rho'] for m in primary_metrics]})")
        if failed_pvalue_count == len(primary_metrics):
            system_failed = True
            system_reasons.append(f"pvalue >= 0.05 for all primary metrics (pvalues: {[reproducibility_results[sys_name][m]['spearman_pvalue'] for m in primary_metrics]})")
        if failed_cv_count == len(primary_metrics):
            system_failed = True
            system_reasons.append(f"CV > 0.5 for all primary metrics (CV values: {[reproducibility_results[sys_name][m]['mean_cv'] for m in primary_metrics]})")
            
        if system_failed:
            validation_passed = False
            for reason in system_reasons:
                fail_reasons.append(f"System '{sys_name}': {reason}")
                
    # Print the reproducibility table
    print("\nREPRODUCIBILITY TABLE:")
    print(f"{'System':<15} | {'Metric':<30} | {'Spearman rho':<12} | {'p-value':<10} | {'Mean CV':<8} | {'Mean CI95 width':<15}")
    print("-" * 105)
    for sys_name in systems_checked:
        for metric in all_metrics:
            m_res = reproducibility_results[sys_name][metric]
            rho = m_res["spearman_rho"]
            pval = m_res["spearman_pvalue"]
            cv = m_res["mean_cv"]
            ci95_w = m_res["mean_ci95_width"]
            print(f"{sys_name:<15} | {metric:<30} | {rho:12.4f} | {pval:10.4e} | {cv:8.4f} | {ci95_w:15.6f}")
    print("-" * 105)
    
    # Save the report
    os.makedirs(REPORT_DIR, exist_ok=True)
    report_data = {
        "metadata": {
            "required_min_points": required_min_points,
            "min_points_found": min_pc,
            "validation_passed": validation_passed,
            "fail_reasons": fail_reasons,
            "systems_checked": systems_checked
        },
        "reproducibility_metrics": reproducibility_results
    }
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"Saved reproducibility report to: {REPORT_FILE}")
    
    if not validation_passed:
        print("\n❌ SCIENTIFIC VALIDATION FAILED")
        for reason in fail_reasons:
            print(f"  - {reason}")
        print("=" * 60)
        sys.exit(1)
    else:
        print("\n✅ SCIENTIFIC VALIDATION PASSED SUCCESSFULLY!")
        print("=" * 60)
        sys.exit(0)

if __name__ == "__main__":
    main()
