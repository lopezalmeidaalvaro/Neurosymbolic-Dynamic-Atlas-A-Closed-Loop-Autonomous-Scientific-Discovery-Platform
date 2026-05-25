"""
Script unificado para generar todas las figuras de los tres papers.
Se conecta al paquete 'neurosymbolic' del repositorio.
Si algún dato real no existe, genera un placeholder.
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# 1. Asegurar que podemos importar 'neurosymbolic'
# ------------------------------------------------------------
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

# ------------------------------------------------------------
# 2. Parámetros y rutas
# ------------------------------------------------------------
os.makedirs("figures", exist_ok=True)

# ------------------------------------------------------------
# PAPER 1: Autonomous Neuro-Symbolic Scientist
# ------------------------------------------------------------
def fig_architecture_diagram():
    """Diagrama de bloques del sistema."""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis('off')
    blocks = [
        (0.5, 2, "Data"),
        (2.5, 2, "Neural Operator Suite\n(NODE, PINN, DeepONet)"),
        (5.5, 2, "Symbolic Distillation\n(SINDy, PySR)"),
        (8.5, 2, "Representation Audit\n(CKA, EV3)"),
    ]
    agent = (5, 3.5, "LLM Orchestrator")
    for (x, y, text) in blocks:
        ax.add_patch(plt.Rectangle((x-1, y-0.8), 2, 1.6, fill=None, edgecolor='black', lw=2))
        ax.text(x, y, text, ha='center', va='center', fontsize=9)
    ax.add_patch(plt.Rectangle((agent[0]-1.2, agent[1]-0.5), 2.4, 1, fill=None, edgecolor='blue', lw=2))
    ax.text(agent[0], agent[1], agent[2], ha='center', va='center', fontsize=9, color='blue')
    ax.annotate('', xy=(1.5,2), xytext=(3.5,2), arrowprops=dict(arrowstyle='->'))
    ax.annotate('', xy=(4.5,2), xytext=(6.5,2), arrowprops=dict(arrowstyle='->'))
    ax.annotate('', xy=(7.5,2), xytext=(9.5,2), arrowprops=dict(arrowstyle='->'))
    ax.annotate('', xy=(5,3), xytext=(5,2.2), arrowprops=dict(arrowstyle='->', color='blue'))
    ax.annotate('', xy=(5,2.2), xytext=(5,3), arrowprops=dict(arrowstyle='->', color='blue'))
    plt.tight_layout()
    plt.savefig("figures/architecture_diagram.pdf")
    plt.close()
    print("-> architecture_diagram.pdf generado")

def fig_cka_ev3():
    """CKA y EV3 por ciclo del orquestador."""
    csv_path = "experiments/lorenz_autonomous_metrics.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        print("AVISO: No se encontró", csv_path, "- usando datos de ejemplo.")
        df = pd.DataFrame({
            'cycle': [1,2,3,4,5],
            'cka': [0.9, 0.8, 0.6, 0.5, 0.4],
            'ev3': [0.6, 0.5, 0.45, 0.4, 0.38]
        })
    fig, ax1 = plt.subplots(figsize=(6,4))
    ax2 = ax1.twinx()
    ax1.plot(df['cycle'], df['cka'], 'b-o', label='CKA')
    ax2.plot(df['cycle'], df['ev3'], 'r-s', label='EV3')
    ax1.set_xlabel('Cycle'); ax1.set_ylabel('CKA', color='b')
    ax2.set_ylabel('EV3', color='r')
    ax1.tick_params(axis='y', labelcolor='b')
    ax2.tick_params(axis='y', labelcolor='r')
    plt.title('Representation audit during autonomous refinement (Lorenz)')
    fig.tight_layout()
    plt.savefig("figures/cka_ev3.pdf")
    plt.close()
    print("-> cka_ev3.pdf generado")

# ------------------------------------------------------------
# PAPER 2: Hybrid Neural ODE–SINDy
# ------------------------------------------------------------
def fig_extrapolation():
    """
    Extrapolación: trayectoria real vs. Neural ODE vs. simbólica.
    Debe cargar experiments/lorenz_extrapolation.npz y graficar las curvas
    extrapoladas reales de la componente X en el intervalo temporal completo [0, 20].
    """
    npz_path = "experiments/lorenz_extrapolation.npz"
    if os.path.exists(npz_path):
        print(f"Cargando datos reales de extrapolación desde {npz_path}...")
        data = np.load(npz_path)
        t = data["t"]
        x_true = data["x_true"][:, 0]  # X-component
        x_node = data["x_node"][:, 0]  # X-component
        x_sym = data["x_sym"][:, 0]    # X-component
        
        if len(x_true) < len(t):
            x_true = np.concatenate([x_true, np.full(len(t) - len(x_true), np.nan)])
        if len(x_node) < len(t):
            x_node = np.concatenate([x_node, np.full(len(t) - len(x_node), np.nan)])
        if len(x_sym) < len(t):
            x_sym = np.concatenate([x_sym, np.full(len(t) - len(x_sym), np.nan)])
            
        t_train_end = 5.0
        
        fig, ax = plt.subplots(figsize=(6,4))
        ax.axvline(t_train_end, color='gray', linestyle=':', label='Training End (t=5)')
        ax.plot(t, x_true, 'k-', label='True')
        ax.plot(t, x_node, 'b--', label='Neural ODE')
        ax.plot(t, x_sym, 'r-.', label='Symbolic')
        
        ax.legend()
        ax.set_xlabel('Time')
        ax.set_ylabel('x')
        plt.title('Long-Term Extrapolation Comparison (Lorenz X-Component)')
        fig.tight_layout()
        plt.savefig("figures/extrapolation.pdf")
        plt.close()
        print("-> extrapolation.pdf generado (datos reales)")
    else:
        print("AVISO: No se encontró", npz_path, "- usando datos de ejemplo.")
        t = np.linspace(0, 20, 1000)
        t_train_end = 5
        x_true = 8 * np.exp(-0.1*t) * np.sin(t) + 2
        x_ode = x_true + 0.5*np.random.randn(len(t))
        x_sym = x_true + 0.1*np.random.randn(len(t))
        mask = t <= t_train_end
        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(t[mask], x_true[mask], 'k.', markersize=3, label='Training')
        ax.plot(t, x_true, 'k-', label='True')
        ax.plot(t, x_ode, 'b--', label='Neural ODE')
        ax.plot(t, x_sym, 'r-', label='Symbolic')
        ax.axvline(t_train_end, color='gray', linestyle=':')
        ax.legend(); ax.set_xlabel('Time'); ax.set_ylabel('x')
        plt.title('Extrapolation on Lorenz system (example)')
        fig.tight_layout()
        plt.savefig("figures/extrapolation.pdf")
        plt.close()
        print("-> extrapolation.pdf generado (ejemplo)")

# ------------------------------------------------------------
# PAPER 3: ECG Representation Audit
# ------------------------------------------------------------
def fig_cka_layers():
    """CKA capa a capa entre modelos pre‑entrenados y fine‑tuneados."""
    matrix_path = "results/cka_layers.npy"
    layers = ['Layer 1', 'Layer 2', 'Layer 3', 'Layer 4', 'Layer 5']
    
    if os.path.exists(matrix_path):
        print(f"Cargando datos de CKA capa a capa desde {matrix_path}...")
        cka_matrix = np.load(matrix_path)
        cka_resnet = cka_matrix[0]
        cka_lstm = cka_matrix[1]
        cka_node = cka_matrix[2]
        
        fig, ax = plt.subplots(figsize=(6,4))
        x = np.arange(len(layers))
        ax.plot(x, cka_resnet, 'o-', color='blue', label='SimpleResNet1D')
        ax.plot(x, cka_lstm, 's-', color='red', label='SimpleLSTM1D')
        ax.plot(x, cka_node, '^-', color='green', label='ECGNeuralODE')
        
        ax.set_xticks(x)
        ax.set_xticklabels(layers)
        ax.set_ylim(-0.05, 1.05)
        ax.set_ylabel('CKA Similarity')
        ax.set_xlabel('Representation Layer')
        ax.legend()
        plt.title('Layer-wise CKA Representation Shift (Base vs Fine-Tuned)')
        fig.tight_layout()
        plt.savefig("figures/cka_layers.pdf")
        plt.close()
        print("-> cka_layers.pdf generado (datos reales)")
    else:
        print("AVISO: No se encontró", matrix_path, "- usando datos de ejemplo.")
        cka_resnet = [0.95, 0.82, 0.61, 0.45, 0.38]
        cka_lstm   = [0.91, 0.78, 0.66, 0.55, 0.42]
        cka_node   = [0.97, 0.93, 0.89, 0.85, 0.78]

        fig, ax = plt.subplots(figsize=(6,4))
        x = np.arange(len(layers))
        ax.plot(x, cka_resnet, 'o-', label='ResNet')
        ax.plot(x, cka_lstm, 's-', label='LSTM')
        ax.plot(x, cka_node, '^-', label='Neural ODE')
        ax.set_xticks(x); ax.set_xticklabels(layers)
        ax.set_ylim(0,1); ax.set_ylabel('CKA'); ax.legend()
        plt.title('Layer-wise CKA (pre-trained vs fine-tuned)')
        fig.tight_layout()
        plt.savefig("figures/cka_layers.pdf")
        plt.close()
        print("-> cka_layers.pdf generado (reemplazar con datos reales)")

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == "__main__":
    print("Generando figuras...")
    fig_architecture_diagram()
    fig_cka_ev3()
    fig_extrapolation()
    fig_cka_layers()
    print("Listo. Revisa la carpeta 'figures/'.")