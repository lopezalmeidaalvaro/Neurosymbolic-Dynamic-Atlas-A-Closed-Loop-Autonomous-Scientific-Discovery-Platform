import os
import matplotlib.pyplot as plt

plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern Roman"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.labelsize": 12,
        "xtick.labelsize": 12,
        "ytick.labelsize": 11,
    }
)

metrics = [
    r"Latent Geometry Collapse" "\n" r"($D_{emb} = 1 - CKA$)",
    r"Attribution Shift" "\n" r"($D_{attr} = 1 - \rho_s$)",
]
values = [0.982, 0.761]
colors = ["#7f7f7f", "#d62728"]

fig, ax = plt.subplots(figsize=(6, 5))
bars = ax.bar(metrics, values, color=colors, width=0.5, alpha=0.85)

for bar, val in zip(bars, values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        val + 0.02,
        rf"\textbf{{{val:.3f}}}",
        ha="center",
        va="bottom",
        fontsize=12,
    )

ax.set_ylabel(r"Deformation Index (Synthetic $\rightarrow$ Clinical)")
ax.set_ylim(0, 1.1)
ax.axhline(1.0, color="black", linestyle="--", alpha=0.3, linewidth=1.5)
ax.text(1.5, 1.02, r"Total Fracture", color="black", alpha=0.5, fontsize=10, ha="right")

plt.tight_layout()

out_dir = "figures"
os.makedirs(out_dir, exist_ok=True)
base_name = os.path.join(out_dir, "fig3_geometry_vs_attribution")
plt.savefig(f"{base_name}.pdf", format="pdf", bbox_inches="tight")
plt.savefig(f"{base_name}.png", format="png", dpi=600, bbox_inches="tight")
plt.close()
print(f"Fig 3 updated in {out_dir}/")
