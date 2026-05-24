"""
Prueba de aislamiento: compara embeddings lorenz noise=0 vs noise=1 seed=42
"""

import json
import sys


def load_lorenz(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    emb = d.get("embeddings", {}).get("lorenz", {})
    seed = d["metadata"].get("seed")
    noise = d["metadata"].get("noiseLevel")
    return emb, seed, noise


base_path = "dashboard/public/artifacts/sessions/lorenz_isolation_noise0_seed42.json"
noisy_path = "dashboard/public/artifacts/sessions/lorenz_isolation_noise1_seed42.json"

emb0, seed0, noise0 = load_lorenz(base_path)
emb1, seed1, noise1 = load_lorenz(noisy_path)

fields = [
    "lyapunov_max",
    "spectral_entropy",
    "dominant_frequency",
    "variance",
    "autocorr_decay",
    "kurtosis",
    "skewness",
    "energy",
]

print(
    f"{'Field':<22} {'noise=0.0 (seed='+str(seed0)+')':<28} {'noise=1.0 (seed='+str(seed1)+')':<28} {'ISOLATED?'}"
)
print("-" * 90)
all_isolated = True
for f in fields:
    v0 = emb0.get(f, None)
    v1 = emb1.get(f, None)
    isolated = v0 != v1
    if not isolated:
        all_isolated = False
    mark = "[OK]" if isolated else "[!!] SAME VALUE"
    print(
        f"  {f:<20} {str(round(v0,6) if v0 else 'N/A'):<28} {str(round(v1,6) if v1 else 'N/A'):<28} {mark}"
    )

print()
print(f"  variance(noise=0): {emb0.get('variance')}")
print(f"  variance(noise=1): {emb1.get('variance')}")
diff = abs(emb1.get("variance", 0) - emb0.get("variance", 0))
print(
    f"  |diff|: {diff:.6f}  {'PASS - embeddings are isolated' if diff > 0 else 'FAIL - embeddings identical'}"
)
print()
if all_isolated:
    print(
        "  RESULT: ALL fields differ between noise=0 and noise=1 [ISOLATION CONFIRMED]"
    )
else:
    print("  RESULT: Some fields are identical [ISOLATION PARTIAL]")
    sys.exit(1)
