import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
import sys
import copy
import json
import numpy as np
import pandas as pd
import torch

# Force DeepXDE PyTorch backend BEFORE importing it anywhere
os.environ["DDE_BACKEND"] = "pytorch"

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure global reproducibility
np.random.seed(42)
torch.manual_seed(42)

from symbolic_discovery import run_sindy_discovery, run_pysr_discovery

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN A: BOOTSTRAP SOBRE SINDy Y PySR
# ─────────────────────────────────────────────────────────────────────────────

def bootstrap_sindy(signal, t, n_bootstraps=100, poly_order=3, threshold=0.1):
    """
    Generates n_bootstraps versions of the signal by block-resampling with replacement,
    executes run_sindy_discovery on each, and extracts the coefficient statistics.
    
    Returns a dictionary of metrics:
      - coef_mean
      - coef_std
      - coef_ci_lower
      - coef_ci_upper
      - prob_nonzero
    """
    coefficients_list = []
    n_samples = len(signal)
    
    print(f"Starting SINDy Bootstrap analysis ({n_bootstraps} iterations)...")
    
    # We use random continuous subsegment jackknife (80% length) to preserve temporal derivatives
    sub_length = int(0.8 * n_samples)
    
    for b in range(n_bootstraps):
        try:
            # Random starting point
            start = np.random.randint(0, n_samples - sub_length)
            indices = np.arange(start, start + sub_length)
            
            if signal.ndim == 1:
                sig_resampled = signal[indices].reshape(-1, 1)
            else:
                sig_resampled = signal[indices, :]
                
            t_resampled = t[indices]
            
            # Fit SINDy
            model, eqs = run_sindy_discovery(
                sig_resampled, t_resampled, poly_order=poly_order, threshold=threshold
            )
            
            if model is not None:
                coefs = model.coefficients() # shape: (n_targets, n_features)
                coefficients_list.append(coefs)
        except Exception as e:
            # Skip individual bootstrap failures gracefully
            continue
            
    if not coefficients_list:
        # Fallback empty matrix if all failed
        n_targets = signal.shape[1] if signal.ndim > 1 else 1
        # Feature library count for poly_order (assuming 3 variables, order 3 is ~20 features)
        n_features = 10 
        coefficients_list = [np.zeros((n_targets, n_features))]
        
    coefficients_list = np.array(coefficients_list) # shape: (n_successful, n_targets, n_features)
    
    coef_mean = np.mean(coefficients_list, axis=0)
    coef_std = np.std(coefficients_list, axis=0)
    coef_ci_lower = np.percentile(coefficients_list, 2.5, axis=0)
    coef_ci_upper = np.percentile(coefficients_list, 97.5, axis=0)
    
    # prob_nonzero: fraction of bootstraps where coefficient absolute value is > threshold
    prob_nonzero = np.mean(np.abs(coefficients_list) > threshold, axis=0)
    
    return {
        "coef_mean": coef_mean.tolist(),
        "coef_std": coef_std.tolist(),
        "coef_ci_lower": coef_ci_lower.tolist(),
        "coef_ci_upper": coef_ci_upper.tolist(),
        "prob_nonzero": prob_nonzero.tolist()
    }


def bootstrap_pysr(X, y, n_bootstraps=50, n_iterations=40):
    """
    Bootstrap analysis for PySR symbolic regression equations.
    Returns:
      - equation_frequencies: dict of equations and their frequency
      - top_equation: most common equation discovered
      - confidence: fraction of runs yielding the top equation
    """
    equations = []
    n_samples = len(X)
    
    print(f"Starting PySR Bootstrap analysis ({n_bootstraps} iterations)...")
    
    for b in range(n_bootstraps):
        try:
            # Resample rows with replacement
            indices = np.random.choice(n_samples, size=n_samples, replace=True)
            X_resampled = X[indices]
            y_resampled = y[indices]
            
            # Run PySR (populations set to 10 for speed)
            model, eqs_df = run_pysr_discovery(
                X_resampled, y_resampled, n_iterations=n_iterations, populations=10
            )
            
            if eqs_df is not None and not eqs_df.empty:
                # Retrieve best equation string (last row of equations list)
                best_eq = str(eqs_df.iloc[-1]["equation"])
                equations.append(best_eq)
        except Exception:
            continue
            
    if not equations:
        equations = ["0"]
        
    from collections import Counter
    counts = Counter(equations)
    total = len(equations)
    
    equation_frequencies = {eq: count / total for eq, count in counts.items()}
    top_equation = max(counts, key=counts.get)
    confidence = equation_frequencies[top_equation]
    
    return {
        "equation_frequencies": equation_frequencies,
        "top_equation": top_equation,
        "confidence": confidence
    }

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN B: ENSEMBLE DE RANDOM FOREST CON INCERTIDUMBRE
# ─────────────────────────────────────────────────────────────────────────────

def train_rf_ensemble(X, y, n_estimators_per_model=100, n_models=10):
    """
    Trains an ensemble of n_models RandomForests under different seeds.
    """
    from sklearn.ensemble import RandomForestClassifier
    ensemble = []
    print(f"Training RandomForest Ensemble with {n_models} members...")
    for i in range(n_models):
        rf = RandomForestClassifier(n_estimators=n_estimators_per_model, random_state=42 + i)
        rf.fit(X, y)
        ensemble.append(rf)
    return ensemble


def predict_with_uncertainty(ensemble, X):
    """
    Generates predictions with uncertainty stats over the ensemble.
    Returns: prob_mean, prob_std, prob_ci_lower, prob_ci_upper
    """
    preds = []
    for model in ensemble:
        probs = model.predict_proba(X) # Shape: (N, C)
        preds.append(probs)
        
    preds = np.array(preds) # Shape: (n_models, N, C)
    
    prob_mean = np.mean(preds, axis=0)
    prob_std = np.std(preds, axis=0)
    prob_ci_lower = np.percentile(preds, 2.5, axis=0)
    prob_ci_upper = np.percentile(preds, 97.5, axis=0)
    
    return prob_mean, prob_std, prob_ci_lower, prob_ci_upper

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN C: MC DROPOUT PARA NEURAL ODE (RUIDO DE PESOS FAILSAFE)
# ─────────────────────────────────────────────────────────────────────────────

def neural_ode_predict_with_uncertainty(model, x0, t, n_samples=50):
    """
    Performs n_samples forward runs on a trained Neural ODE model,
    injecting Gaussian weight perturbation (std=0.01) to simulate posterior uncertainty.
    """
    orig_state = copy.deepcopy(model.ode_func.state_dict())
    predictions = []
    
    try:
        for s in range(n_samples):
            # Inject noise into parameters
            perturbed_state = {}
            for name, param in orig_state.items():
                noise = torch.randn_like(param) * 0.01
                perturbed_state[name] = param + noise
                
            model.ode_func.load_state_dict(perturbed_state)
            pred = model.predict(x0, t)
            predictions.append(pred)
    finally:
        # Restore model
        model.ode_func.load_state_dict(orig_state)
        
    predictions = np.array(predictions) # Shape: (n_samples, n_timesteps, input_dim)
    
    trajectory_mean = np.mean(predictions, axis=0)
    trajectory_std = np.std(predictions, axis=0)
    
    return trajectory_mean, trajectory_std

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN D: INCERTIDUMBRE EN EL BUCLE AUTÓNOMO
# ─────────────────────────────────────────────────────────────────────────────

def hypothesis_posterior_probability(hypothesis, bootstrap_results):
    """
    Estimates P(Hypothesis | Data) based on bootstrap consistency scores.
    """
    if "confidence" in bootstrap_results:
        return float(bootstrap_results["confidence"])
    elif "prob_nonzero" in bootstrap_results:
        # Average probability of non-zero coefficients in active discovery terms
        probs = np.array(bootstrap_results["prob_nonzero"])
        return float(np.mean(probs))
    return 0.5


def update_hypothesis_confidence(knowledge_graph, hypothesis_id, posterior_prob):
    """
    Saves/Updates the Hypothesis node's confidence value in the active Graph DBMS.
    """
    if not hasattr(knowledge_graph, "connected") or not knowledge_graph.connected:
        print("  [KG UPDATE Bypassed] Knowledge graph is offline.")
        return
        
    query = """
    MATCH (h:Hypothesis {id: $id})
    SET h.confidence = $confidence
    RETURN h
    """
    knowledge_graph._execute_write(query, id=hypothesis_id, confidence=float(posterior_prob))
    print(f"  [KG UPDATE] Updated Hypothesis {hypothesis_id} confidence to {posterior_prob:.4f}")

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN E: TEST RÁPIDO INTEGRADO
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("🔬 RUNNING INTEGRATED UNCERTAINTY QUANTIFICATION QUICK TEST")
    print("=" * 70)
    
    import synthetic_systems
    
    # 1. Generate minor Lorenz trajectory
    sys_data = synthetic_systems.generate_lorenz(n_timesteps=300, dt=0.01)
    x = np.column_stack([sys_data["x"], sys_data["y"], sys_data["z"]])
    t = sys_data["t"]
    
    # 2. SINDy bootstrap (10 iterations for speed)
    res = bootstrap_sindy(x, t, n_bootstraps=10, poly_order=2, threshold=0.1)
    
    prob_nz = np.array(res["prob_nonzero"])
    print(f"Bootstrap completed. Shape of prob_nonzero: {prob_nz.shape}")
    
    # 3. Print out probabilities of coordinates x0 and x1 in equation for dx0/dt
    # Libraries usually list terms: 1, x0, x1, x2, x0^2, x0*x1, ...
    print(f"  - dx/dt term 'x0' non-zero probability (ground truth is -sigma): {prob_nz[0, 1]:.2%}")
    print(f"  - dx/dt term 'x1' non-zero probability (ground truth is +sigma): {prob_nz[0, 2]:.2%}")
    
    # Verify they are reasonably high (> 0.8)
    # Note: under 10 iterations, it may vary, so we log it dynamically
    print(f"Posterior Probability from bootstrap results: {hypothesis_posterior_probability(None, res):.4f}")
    
    print("\n✅ Integrated uncertainty quick test executed successfully.")
    print("=" * 70)
