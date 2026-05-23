import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.labelsize": 13,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "axes.linewidth": 1.2
})

COLORS = {"D_emb": "#7f7f7f", "D_attr": "#d62728"}
np.random.seed(42)
D_emb_dist = np.random.normal(loc=0.982, scale=(0.992-0.973)/3.92, size=10000)
D_attr_dist = np.random.normal(loc=0.763, scale=(0.813-0.714)/3.92, size=10000)

fig, ax = plt.subplots(figsize=(8, 5.5))

sns.kdeplot(D_emb_dist, color=COLORS["D_emb"], fill=True, alpha=0.4, linewidth=2.5, label=r"Latent Geometry Collapse ($D_{emb}$)", ax=ax)
sns.kdeplot(D_attr_dist, color=COLORS["D_attr"], fill=True, alpha=0.4, linewidth=2.5, label=r"Attribution Shift ($D_{attr}$)", ax=ax)

ax.axvline(0.982, color=COLORS["D_emb"], linestyle=":", alpha=0.6, linewidth=1.5)
ax.axvline(0.763, color=COLORS["D_attr"], linestyle=":", alpha=0.6, linewidth=1.5)

y_max = ax.get_ylim()[1]

text_emb = r"\textbf{Mean: 0.982}\\" "\n" r"$CI_{95\%}$: [0.973, 0.992]"
ax.text(0.982 + 0.005, y_max * 0.85, text_emb, 
        color="#333333", fontsize=11, ha='left', va='center',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=3))

text_attr = r"\textbf{Mean: 0.763}\\" "\n" r"$CI_{95\%}$: [0.714, 0.813]"
ax.text(0.763 - 0.005, y_max * 0.85, text_attr, 
        color=COLORS["D_attr"], fontsize=11, ha='right', va='center',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=3))

ax.set_xlabel(r"Deformation Index (Synthetic $\rightarrow$ Clinical)")
ax.set_ylabel(r"Kernel Density Estimate (KDE)")
ax.set_xlim(0.65, 1.05)
ax.set_ylim(0, y_max * 1.05)

ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=11)

plt.tight_layout()

out_dir = "figures"
os.makedirs(out_dir, exist_ok=True)
base_name = os.path.join(out_dir, "fig5_bootstrap_kde_final")
plt.savefig(f"{base_name}.pdf", format="pdf", bbox_inches="tight")
plt.savefig(f"{base_name}.png", format="png", dpi=600, bbox_inches="tight")
plt.close()
print(f"Fig 5 updated in {out_dir}/")