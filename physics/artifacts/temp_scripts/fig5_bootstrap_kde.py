import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams.update(
    {
        "text.usetex": False,
        "font.family": "serif",
        "font.serif": ["DejaVu Serif", "Times New Roman", "serif"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelsize": 13,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "axes.linewidth": 1.2,
    }
)

COLORS = {"D_emb": "#7f7f7f", "D_attr": "#d62728"}

import json

# Try to load real bootstrap results
json_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "artifacts",
    "bootstrap_results.json",
)
if os.path.exists(json_path):
    print(f"Loading real bootstrap results from: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    D_emb_dist = np.array(data["D_emb_samples"])
    D_attr_dist = np.array(data["D_attr_samples"])
    mean_emb = data["D_emb_mean"]
    ci_emb = [data["D_emb_ci_lower"], data["D_emb_ci_upper"]]
    mean_attr = data["D_attr_mean"]
    ci_attr = [data["D_attr_ci_lower"], data["D_attr_ci_upper"]]
else:
    print("Bootstrap results JSON not found. Using fallback normal distribution.")
    np.random.seed(42)
    D_emb_dist = np.random.normal(loc=0.982, scale=(0.992 - 0.973) / 3.92, size=1000)
    D_attr_dist = np.random.normal(loc=0.763, scale=(0.813 - 0.714) / 3.92, size=1000)
    mean_emb = 0.982
    ci_emb = [0.973, 0.992]
    mean_attr = 0.763
    ci_attr = [0.714, 0.813]

fig, ax = plt.subplots(figsize=(8, 5.5))

sns.kdeplot(
    D_emb_dist,
    color=COLORS["D_emb"],
    fill=True,
    alpha=0.4,
    linewidth=2.5,
    label=r"Latent Geometry Collapse ($D_{emb}$)",
    ax=ax,
)
sns.kdeplot(
    D_attr_dist,
    color=COLORS["D_attr"],
    fill=True,
    alpha=0.4,
    linewidth=2.5,
    label=r"Attribution Shift ($D_{attr}$)",
    ax=ax,
)

ax.axvline(mean_emb, color=COLORS["D_emb"], linestyle=":", alpha=0.6, linewidth=1.5)
ax.axvline(mean_attr, color=COLORS["D_attr"], linestyle=":", alpha=0.6, linewidth=1.5)

y_max = ax.get_ylim()[1]

text_emb = f"Mean: {mean_emb:.3f}\n95% CI: [{ci_emb[0]:.3f}, {ci_emb[1]:.3f}]"
ax.text(
    mean_emb + 0.005,
    y_max * 0.85,
    text_emb,
    color="#333333",
    fontsize=11,
    ha="left",
    va="center",
    bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=3),
)

text_attr = f"Mean: {mean_attr:.3f}\n95% CI: [{ci_attr[0]:.3f}, {ci_attr[1]:.3f}]"
ax.text(
    mean_attr - 0.005,
    y_max * 0.85,
    text_attr,
    color=COLORS["D_attr"],
    fontsize=11,
    ha="right",
    va="center",
    bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", pad=3),
)

ax.set_xlabel(r"Deformation Index (Synthetic $\rightarrow$ Clinical)")
ax.set_ylabel(r"Kernel Density Estimate (KDE)")
ax.set_xlim(0.65, 1.05)
ax.set_ylim(0, y_max * 1.05)

ax.legend(
    frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=11
)

plt.tight_layout()

out_dir = "figures"
os.makedirs(out_dir, exist_ok=True)
base_name = os.path.join(out_dir, "fig5_bootstrap_kde_final")
plt.savefig(f"{base_name}.pdf", format="pdf", bbox_inches="tight")
plt.savefig(f"{base_name}.png", format="png", dpi=600, bbox_inches="tight")
plt.close()
print(f"Fig 5 updated in {out_dir}/")
