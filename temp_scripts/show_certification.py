import json

with open('dashboard/public/artifacts/discoveries/massive_sweep_report.json', encoding='utf-8') as f:
    report = json.load(f)

print("=== METADATA ===")
meta = report['metadata']
print(f"  seeds:                     {meta['seeds']}")
print(f"  certification_schema_version: {meta['certification_schema_version']}")
print(f"  confidence_method:         {meta['confidence_method']}")
print(f"  noise_levels count:        {len(meta['noise_levels'])}")
print()

print("=== CERTIFIED_RESULTS (lorenz) ===")
certified = report.get('certified_results', [])
lorenz_cr = next((r for r in certified if r.get('system') == 'lorenz'), None)
if lorenz_cr:
    print(f"  system: {lorenz_cr['system']}")
    print(f"  noise:       {lorenz_cr['noise']}")
    print(f"  mean_drift:  {lorenz_cr['mean_drift']}")
    print(f"  velocity:    {lorenz_cr['velocity']}")
    print(f"  acceleration:{lorenz_cr['acceleration']}")
    cert = lorenz_cr['certification']
    print()
    print("  --- certification block ---")
    print(json.dumps(cert, indent=4))
else:
    print("  lorenz NOT FOUND in certified_results")
    print("  Keys present:", [r.get('system') for r in certified])

print()
print("=== CERTIFIED_RESULTS (rossler) ===")
rossler_cr = next((r for r in certified if r.get('system') == 'rossler'), None)
if rossler_cr:
    cert_r = rossler_cr['certification']
    print(f"  system: {rossler_cr['system']}")
    print("  --- certification block ---")
    print(json.dumps(cert_r, indent=4))

print()
print("=== STRUCTURE VALIDATION ===")
print(f"  Top-level keys: {list(report.keys())}")
has_legacy = 'certification' in report
print(f"  Legacy 'certification' key present: {has_legacy}  (should be False)")
print(f"  certified_results is list: {isinstance(certified, list)}")
print(f"  certified_results count: {len(certified)}")
