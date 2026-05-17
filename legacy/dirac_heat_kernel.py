"""
ITERACION 2: Regulador Espectral Dinamico via Funcion de Calor del Operador de Dirac
Framework: Covariancia de Resonancia Topologica (TRC) — Pivote UV/IR

El codigo construye el operador de Dirac D en 2D (matrices gamma de Pauli),
calcula D^2 explicitamente, y evalua Tr(exp(-s*D^2)) via diagonalizacion
numerica real. El Hamiltoniano efectivo se deriva del resultado, no al reves.
"""

import sympy as sp
import numpy as np

def build_dirac_operator():
    """
    Construye el operador de Dirac D = gamma^mu * p_mu en 2D
    usando las matrices gamma de Pauli como representacion clifford.
    
    Representacion:
      gamma^0 = sigma_z = diag(1, -1)
      gamma^1 = i * sigma_y = [[0, 1], [-1, 0]]
    
    Para un estado de momento (p0, p1) discreto en la red de Planck.
    """
    p0, p1 = sp.symbols('p0 p1', real=True)
    m = sp.symbols('m', real=True, positive=True)

    # Matrices gamma en 2D (representacion de Weyl)
    gamma0 = sp.Matrix([[1, 0], [0, -1]])          # gamma^0 = sigma_z
    gamma1 = sp.Matrix([[0, 1], [-1, 0]])           # gamma^1 = i*sigma_y

    # Operador de Dirac masivo: D = gamma^mu * p_mu - m*I
    D = gamma0 * p0 + gamma1 * p1 - m * sp.eye(2)

    print("Operador de Dirac D (simbolico):")
    sp.pprint(D)
    print()
    return D, p0, p1, m


def compute_D_squared(D, p0, p1, m):
    """
    Calcula D^2 = D * D explicitamente sin simplificacion manual.
    El resultado es lo que la algebra matricial produce, no lo que
    la teoria predice.
    """
    D2 = D * D
    D2_simplified = sp.simplify(D2)
    print("D^2 = D * D (resultado bruto de la algebra matricial):")
    sp.pprint(D2_simplified)
    print()
    return D2_simplified


def heat_kernel_trace_numeric(D2_sym, p0, p1, m, s_values, p0_val, p1_val, m_val):
    """
    Calcula Tr(exp(-s * D^2)) mediante sustitucion numerica y
    diagonalizacion real de la matriz D^2.
    
    PROCESO:
      1. Sustituir valores numericos en D^2
      2. Convertir a numpy para eigendecomposicion
      3. Traza = sum_i exp(-s * lambda_i)
      
    Si algun eigenvalor es negativo (violacion de positividad espectral),
    se detecta y reporta como anomalia de unitariedad.
    """
    # Sustituir valores numericos
    D2_num = D2_sym.subs([(p0, p0_val), (p1, p1_val), (m, m_val)])
    D2_matrix = np.array(D2_num.tolist(), dtype=complex)

    eigenvalues = np.linalg.eigvalsh(D2_matrix.real)  # D^2 debe ser hermitiano

    print(f"Eigenvalores de D^2 en (p0={p0_val}, p1={p1_val}, m={m_val}):")
    for i, ev in enumerate(eigenvalues):
        print(f"  lambda_{i} = {ev:.6f}")

    # DETECCION DE ANOMALIA: eigenvalores negativos => positividad espectral violada
    negative_eigs = [ev for ev in eigenvalues if ev < 0]
    if negative_eigs:
        print(f"\n[ANOMALIA DETECTADA] Eigenvalores negativos: {negative_eigs}")
        print("=> Positividad espectral violada. Unitariedad de S-matrix: COMPROMETIDA\n")
    else:
        print("\nEigenvalores positivos. Positividad espectral local: OK\n")

    # Calcular traza del heat kernel para cada valor de s
    print("s           | Tr(exp(-s*D^2))  | Interpretacion")
    print("-" * 60)
    
    traces = []
    for s in s_values:
        trace_val = np.sum(np.exp(-s * eigenvalues))
        traces.append((s, trace_val))
        
        if s < 1e-10:
            interpretation = "Limite UV (s->0): divergencia esperada"
        elif s > 1e4:
            interpretation = "Limite IR (s->inf): supresion exponencial"
        else:
            interpretation = "Regimen intermedio"
        
        print(f"{s:<12.2e} | {trace_val:<16.6f} | {interpretation}")
    
    return eigenvalues, traces


def derive_effective_hamiltonian(traces, s_values):
    """
    Deriva el Hamiltoniano efectivo H_eff desde la traza del heat kernel:
      H_eff = -d/ds ln(Tr(exp(-s*D^2))) |_{s=s_0}
    
    Esto es un calculo directo de la derivada de la funcion de particion espectral.
    No se impone ninguna forma funcional a priori.
    """
    print("\nDerivacion del Hamiltoniano Efectivo H_eff = -d/ds [ln K(s)]:")
    print("-" * 60)
    
    # Solo calcular donde la traza es positiva (unitaria)
    ln_traces = []
    for s, tr in traces:
        if tr.real > 0:
            ln_traces.append((s, np.log(tr.real)))
        else:
            print(f"  s={s:.2e}: Traza no-positiva ({tr:.4f}) => ln indefinido => ANOMALIA UNITARIA")
            ln_traces.append((s, None))
    
    print("\ns           | H_eff = -d(ln K)/ds  | Estatus")
    print("-" * 60)
    
    for i in range(1, len(ln_traces) - 1):
        s_prev, lk_prev = ln_traces[i-1]
        s_next, lk_next = ln_traces[i+1]
        s_curr, lk_curr = ln_traces[i]
        
        if lk_prev is None or lk_next is None:
            print(f"  s={s_curr:.2e}: H_eff indefinido (anomalia en vecindad)")
            continue
        
        ds = s_next - s_prev
        d_ln_K = (lk_next - lk_prev) / ds
        H_eff = -d_ln_K
        
        # Deteccion de H_eff negativo => violacion de positividad energetica
        status = "OK" if H_eff > 0 else "[ANOMALIA: H_eff < 0 => vacuum decay]"
        print(f"  s={s_curr:.2e}: H_eff = {H_eff:.4f}  {status}")


def analyze_unitarity(eigenvalues, s_ref=1.0):
    """
    Test de unitariedad de la S-matrix via condicion de óptico:
    
    La S-matrix es unitaria si el propagador espectral K(s) satisface:
      2 * Im(A_forward) = integral de secciones eficaces totales (Teorema Optico)
    
    En nuestro espacio discreto, el discriminante de unitariedad es:
      U = Tr(exp(-s*D^2)) - dim(H)
    
    Si U > 0: over-complete (violacion por exceso de estados)
    Si U = 0: unitario
    Si U < 0: perdida de estados (violacion por defecto)
    """
    dim_H = len(eigenvalues)
    K_ref = np.sum(np.exp(-s_ref * eigenvalues))
    U = K_ref - dim_H
    
    print(f"\nTest de Unitariedad de la S-matrix (s_ref = {s_ref}):")
    print(f"  dim(H) = {dim_H}")
    print(f"  K(s_ref) = Tr(exp(-s*D^2)) = {K_ref:.6f}")
    print(f"  Discriminante U = K - dim(H) = {U:.6f}")
    
    if abs(U) < 1e-6:
        verdict = "UNITARIA: S-matrix conserva probabilidad total"
    elif U > 0:
        verdict = "[VIOLACION]: Over-completeness => nuevos estados fantasma (ghost states)"
    else:
        verdict = "[VIOLACION]: Perdida de estados => no-unitariedad disipativa"
    
    print(f"  Veredicto: {verdict}")
    return U, verdict


# ============================================================
# EJECUCION PRINCIPAL
# ============================================================

print("=" * 70)
print("ITERACION 2: REGULADOR ESPECTRAL — FUNCION DE CALOR DEL OPERADOR DE DIRAC")
print("=" * 70)
print()

# 1. Construccion del operador de Dirac
D, p0, p1, m = build_dirac_operator()

# 2. Calculo de D^2 (puro algebra matricial)
D2 = compute_D_squared(D, p0, p1, m)

# 3. Evaluacion numerica del heat kernel Tr(exp(-s*D^2))
# Valores en unidades de Planck (l_P = 1): p0=1, p1=0.5, m=0.1
p0_val, p1_val, m_val = 1.0, 0.5, 0.1

# Barrido logaritmico de s: UV (s->0) a IR (s->inf)
s_values = [1e-8, 1e-4, 1e-2, 1e-1, 1.0, 1e1, 1e3, 1e6]

eigenvalues, traces = heat_kernel_trace_numeric(
    D2, p0, p1, m, s_values, p0_val, p1_val, m_val
)

# 4. Derivacion del Hamiltoniano efectivo
derive_effective_hamiltonian(traces, s_values)

# 5. Test de unitariedad de la S-matrix
U, verdict = analyze_unitarity(eigenvalues, s_ref=1.0)

print()
print("=" * 70)
print("FIN DEL CALCULO ESPECTRAL")
print("=" * 70)
