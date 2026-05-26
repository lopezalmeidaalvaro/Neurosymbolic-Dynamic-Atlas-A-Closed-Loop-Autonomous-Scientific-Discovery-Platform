import os
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
        # AÑADIDO: Cargar paquetes matemáticos para \mathbb
        "text.latex.preamble": r"\usepackage{amsfonts} \usepackage{amsmath}",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelsize": 12,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "lines.linewidth": 2.5,
        "lines.markersize": 8,
    }
)

COLORS = {
    "Synthetic": "#1f77b4",
    "Biophysical": "#ff7f0e",
    "Clinical": "#d62728",
    "Null": "#7f7f7f",
}

domains = [
    r"\textbf{Synthetic}" + "\n" + r"\textbf{Chaos}",
    r"\textbf{Composite}" + "\n" + r"\textbf{Biophysical}",
    r"\textbf{Clinical}" + "\n" + r"\textbf{ECG}",
]
x = np.array([0, 1, 2])

features = {
    r"$H_{perm}$": [0.45, 0.15, 0.05],
    r"$H_{SVD}$": [0.10, 0.35, 0.40],
    r"$\tau_{acf}$": [0.05, 0.20, 0.25],
    r"$I_{temp}$": [0.20, 0.15, 0.10],
    r"Others": [0.20, 0.15, 0.20],
}

fig, ax = plt.subplots(figsize=(8, 6))

for feat, vals in features.items():
    if feat == r"$H_{perm}$":
        color, alpha, lw = COLORS["Synthetic"], 1.0, 3.5
    elif feat == r"$H_{SVD}$":
        color, alpha, lw = COLORS["Clinical"], 1.0, 3.5
    elif feat == r"$\tau_{acf}$":
        color, alpha, lw = COLORS["Biophysical"], 1.0, 3.5
    else:
        color, alpha, lw = COLORS["Null"], 0.5, 1.5

    ax.plot(x, vals, marker="o", color=color, alpha=alpha, linewidth=lw)

    label = rf"\textbf{{{feat}}}" if alpha == 1.0 else feat
    ax.text(x[-1] + 0.05, vals[-1], label, color=color, fontsize=12, va="center")

ax.set_xticks(x)
ax.set_xticklabels(domains)
ax.set_ylabel(r"Expected Attribution $\mathbb{E}[C]$")
ax.set_xlim(-0.2, 2.5)
ax.set_ylim(0, 0.5)

plt.tight_layout()

out_dir = "figures"
os.makedirs(out_dir, exist_ok=True)
base_name = os.path.join(out_dir, "fig2_causal_reranking")
plt.savefig(f"{base_name}.pdf", format="pdf", bbox_inches="tight")
plt.savefig(f"{base_name}.png", format="png", dpi=600, bbox_inches="tight")
plt.close()
print(f"✅ Fig 2 updated in {out_dir}/")
