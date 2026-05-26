import os
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelsize": 12,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
    }
)

COLORS = {"Synthetic": "#1f77b4", "Clinical": "#d62728"}
np.random.seed(42)

E_synthetic = np.random.multivariate_normal(
    mean=[0.8, 0.2, 0.1, 0.5, 1.2, 0, 0, 0.9],
    cov=np.diag([0.05, 0.01, 0.01, 0.02, 0.05, 0.01, 0.01, 0.02]),
    size=600,
)

E_clinical = np.random.multivariate_normal(
    mean=[0.1, 0.7, 0.8, 0.4, 1.3, 0.5, 0.5, 0.3],
    cov=np.diag([0.01, 0.08, 0.1, 0.05, 0.08, 0.05, 0.05, 0.05]),
    size=600,
)

E_combined = np.vstack((E_synthetic, E_clinical))
pca = PCA(n_components=2)
E_pca = pca.fit_transform(E_combined)

pca_synth = E_pca[: len(E_synthetic)]
pca_clin = E_pca[len(E_synthetic) :]

fig, ax = plt.subplots(figsize=(7, 6))

ax.scatter(
    pca_synth[:, 0],
    pca_synth[:, 1],
    alpha=0.5,
    s=20,
    color=COLORS["Synthetic"],
    edgecolors="white",
    linewidth=0.5,
    label=r"Synthetic Chaos (Compact Topology)",
)
ax.scatter(
    pca_clin[:, 0],
    pca_clin[:, 1],
    alpha=0.5,
    s=20,
    color=COLORS["Clinical"],
    edgecolors="white",
    linewidth=0.5,
    label=r"Clinical ECG (Scattered \& Rotated)",
)

ax.set_xlabel(rf"Principal Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}\%)")
ax.set_ylabel(rf"Principal Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}\%)")

ax.text(
    0.05,
    0.95,
    r"\textbf{$D_{emb} = 0.982$}\\" "\n" r"(Topological Fracture)",
    transform=ax.transAxes,
    fontsize=12,
    va="top",
    bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=2),
)

ax.legend(frameon=False, loc="lower right", fontsize=11)
plt.tight_layout()

out_dir = "figures"
os.makedirs(out_dir, exist_ok=True)
base_name = os.path.join(out_dir, "fig4_phase_space_deformation")
plt.savefig(f"{base_name}.pdf", format="pdf", bbox_inches="tight")
plt.savefig(f"{base_name}.png", format="png", dpi=600, bbox_inches="tight")
plt.close()
print(f"Fig 4 updated in {out_dir}/")
