import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "axes.spines.bottom": False
})

COLORS = {
    "Synthetic": "#1f77b4",
    "Biophysical": "#ff7f0e",
    "Clinical": "#d62728",
    "Null": "#7f7f7f"
}

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.set_xticks([])
ax.set_yticks([])

def draw_box(ax, x, y, width, height, text, color):
    box = patches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.1", 
                                 ec=color, fc="white", lw=2.5, zorder=3)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text, ha='center', va='center', 
            fontsize=11, color=color, zorder=4)
    return x + width/2, y + height/2, x, x + width, y, y + height

w, h = 1.8, 0.8
cx_A, cy_A, l_A, r_A, b_A, t_A = draw_box(ax, 1, 4, w, h, r"\textbf{Domain A}" + "\n" + "Synthetic Chaos", COLORS["Synthetic"])
cx_B, cy_B, l_B, r_B, b_B, t_B = draw_box(ax, 4.1, 4, w, h, r"\textbf{Domain B}" + "\n" + "Composite Biophysical", COLORS["Biophysical"])
cx_C, cy_C, l_C, r_C, b_C, t_C = draw_box(ax, 7.2, 4, w, h, r"\textbf{Domain C}" + "\n" + "Clinical ECG", COLORS["Clinical"])
cx_N, cy_N, l_N, r_N, b_N, t_N = draw_box(ax, 4.1, 1.5, w, h, r"\textbf{Domain N}" + "\n" + "Null Control", COLORS["Null"])

def draw_arrow(ax, x1, y1, x2, y2, text, color="black", rad=0.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=2, connectionstyle=f"arc3,rad={rad}"), zorder=1)
    
    if rad == 0:
        tx, ty = (x1+x2)/2, (y1+y2)/2
    else:
        tx, ty = (x1+x2)/2, (y1+y2)/2 + (0.5 if rad < 0 else -0.5)
        
    ax.text(tx, ty + 0.2, text, ha='center', va='center', fontsize=11, 
            bbox=dict(facecolor='white', edgecolor='none', pad=1), zorder=2)

draw_arrow(ax, r_A, cy_A, l_B, cy_B, r"$S_1 = -0.14$")
draw_arrow(ax, r_B, cy_B, l_C, cy_C, r"$S_2 = 0.66$")
draw_arrow(ax, cx_A, t_A, cx_C, t_C, r"$S_3 = 0.26 \mid D_{emb} = 0.98 \mid D_{attr} = 0.76$", rad=-0.3)
draw_arrow(ax, cx_A+0.4, b_A, l_N, cy_N+0.2, r"$S_1^{null} = 0.47$", color=COLORS["Null"])
draw_arrow(ax, r_N, cy_N+0.2, cx_C-0.4, b_C, r"$S_2^{null} = 0.16$", color=COLORS["Null"])

# Corrección visual: Sustituimos el "Falsification Rejected" por el dato neutral
ax.text(5, 0.5, r"\textbf{Transition Audit:} $\Delta K = -0.051 \ (p = 0.168)$", 
        ha='center', va='center', fontsize=12,
        bbox=dict(facecolor='#f0f0f0', edgecolor=COLORS["Null"], lw=1.5, pad=5))

plt.tight_layout()

out_dir = "figures"
os.makedirs(out_dir, exist_ok=True)
base_name = os.path.join(out_dir, "fig1_epistemological_pipeline")
plt.savefig(f"{base_name}.pdf", format="pdf", bbox_inches="tight")
plt.savefig(f"{base_name}.png", format="png", dpi=600, bbox_inches="tight")
plt.close()
print(f"Fig 1 updated in {out_dir}/")