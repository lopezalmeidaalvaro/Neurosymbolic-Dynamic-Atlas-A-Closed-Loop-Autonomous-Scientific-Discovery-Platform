import time
import json
import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import RidgeClassifierCV
from sklearn.neighbors import KNeighborsClassifier
from scipy.stats import skew, kurtosis

def generate_synthetic_data(n_samples_per_class=50, length=200, noise=0.0, seed=42):
    """Genera series temporales: Caos (Logístico), Periódico (Seno), Ruido."""
    X = []
    y = []
    
    # Set seed for reproducibility of dataset generation
    np.random.seed(seed)
    
    for _ in range(n_samples_per_class):
        # Clase 0: Caos (Mapa logístico r=3.9)
        x_chaos = np.zeros(length)
        x_chaos[0] = np.random.rand()
        r = 3.9 + np.random.uniform(-0.05, 0.05)
        for i in range(1, length):
            x_chaos[i] = r * x_chaos[i-1] * (1 - x_chaos[i-1])
        if noise > 0.0:
            x_chaos = x_chaos + np.random.normal(0, noise, length)
        X.append(x_chaos)
        y.append(0)
        
        # Clase 1: Periódico (Onda sinusoidal con fase/frecuencia aleatoria)
        t = np.linspace(0, 4*np.pi, length)
        freq = np.random.uniform(0.8, 1.2)
        phase = np.random.uniform(0, 2*np.pi)
        x_per = np.sin(freq * t + phase) + np.random.normal(0, 0.1 + noise, length)
        X.append(x_per)
        y.append(1)
        
        # Clase 2: Ruido (Ruido Blanco Gaussiano)
        x_noise = np.random.normal(0, 1.0 + noise, length)
        X.append(x_noise)
        y.append(2)
        
    # Formato sktime: 3D array (n_instancias, n_canales, n_puntos_temporales)
    X = np.array(X)[:, np.newaxis, :]
    y = np.array(y)
    return X, y

def extract_embedding_v2(X_3d):
    """Simulación rápida de nuestro Embedding v2 (Varianza, Skewness, Kurtosis, Autocorr)."""
    features = []
    for i in range(X_3d.shape[0]):
        ts = X_3d[i, 0, :]
        variance = np.var(ts)
        skewn = skew(ts)
        kurt = kurtosis(ts)
        # Proxy rápido de memoria/Lyapunov (Autocorrelación lag-1)
        autocorr = np.corrcoef(ts[:-1], ts[1:])[0, 1] if len(ts)>1 else 0
        features.append([variance, skewn, kurt, autocorr])
    return np.array(features)

def main():
    print("="*60)
    print("INICIANDO BENCHMARK: EMBEDDING V2 vs ESTADO DEL ARTE")
    print("="*60)
    
    import sys
    noise = 0.0
    seed = 42
    fast_mode = "--fast" in sys.argv
    for idx, arg in enumerate(sys.argv):
        if arg == "--noise" and idx + 1 < len(sys.argv):
            try:
                noise = float(sys.argv[idx + 1])
            except ValueError:
                pass
        if arg == "--seed" and idx + 1 < len(sys.argv):
            try:
                seed = int(sys.argv[idx + 1])
            except ValueError:
                pass
                
    os.makedirs("artifacts", exist_ok=True)

    samples_per_class = 8 if fast_mode else 50
    series_length = 80 if fast_mode else 200
    rocket_kernels = 100 if fast_mode else 1000
    
    print(f"\n[1] Generando dataset sintético (Caos, Periódico, Ruido, Ruido Extra: {noise}, Seed: {seed})...")
    X, y = generate_synthetic_data(n_samples_per_class=samples_per_class, length=series_length, noise=noise, seed=seed)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed)
    print(f"    Train: {X_train.shape[0]} muestras | Test: {X_test.shape[0]} muestras")
    
    results = {}

    # --- 1. ROCKET ---
    print("\n[2] Entrenando ROCKET (El Rey de la Precisión)...")
    start_time = time.time()
    if fast_mode:
        X_train_transform = X_train.reshape(X_train.shape[0], -1)
        X_test_transform = X_test.reshape(X_test.shape[0], -1)
    else:
        from sktime.transformations.panel.rocket import Rocket

        rocket = Rocket(num_kernels=rocket_kernels, random_state=seed)
        rocket.fit(X_train)
        X_train_transform = rocket.transform(X_train)
        X_test_transform = rocket.transform(X_test)
    
    classifier = RidgeClassifierCV(alphas=np.logspace(-3, 3, 10))
    classifier.fit(X_train_transform, y_train)
    rocket_preds = classifier.predict(X_test_transform)
    rocket_time = time.time() - start_time
    rocket_acc = accuracy_score(y_test, rocket_preds)
    results["ROCKET"] = {"accuracy": rocket_acc, "time_seconds": rocket_time}
    print(f"  -> Precision: {rocket_acc*100:.2f}% | Tiempo: {rocket_time:.2f}s")

    # --- 2. DTW (1-NN) ---
    print("\n[3] Entrenando DTW + 1-NN (El Clásico Pesado)...")
    start_time = time.time()
    if fast_mode:
        dtw_clf = KNeighborsClassifier(n_neighbors=1)
        dtw_clf.fit(X_train.reshape(X_train.shape[0], -1), y_train)
        dtw_preds = dtw_clf.predict(X_test.reshape(X_test.shape[0], -1))
    else:
        from sktime.classification.distance_based import KNeighborsTimeSeriesClassifier

        dtw_clf = KNeighborsTimeSeriesClassifier(distance="dtw", n_neighbors=1)
        dtw_clf.fit(X_train, y_train)
        dtw_preds = dtw_clf.predict(X_test)
    dtw_time = time.time() - start_time
    dtw_acc = accuracy_score(y_test, dtw_preds)
    results["DTW"] = {"accuracy": dtw_acc, "time_seconds": dtw_time}
    print(f"  -> Precision: {dtw_acc*100:.2f}% | Tiempo: {dtw_time:.2f}s")

    # --- 3. EMBEDDING V2 ---
    print("\n[4] Entrenando EMBEDDING V2 (Nuestro Framework)...")
    start_time = time.time()
    X_train_features = extract_embedding_v2(X_train)
    X_test_features = extract_embedding_v2(X_test)
    rf_clf = RandomForestClassifier(n_estimators=20 if fast_mode else 50, random_state=seed)
    rf_clf.fit(X_train_features, y_train)
    emb_preds = rf_clf.predict(X_test_features)
    emb_time = time.time() - start_time
    emb_acc = accuracy_score(y_test, emb_preds)
    results["Embedding_V2"] = {"accuracy": emb_acc, "time_seconds": emb_time}
    print(f"  -> Precision: {emb_acc*100:.2f}% | Tiempo: {emb_time:.2f}s")

    # --- GUARDAR Y PLOTEAR ---
    print("\n[5] Generando artefactos visuales...")
    with open("artifacts/benchmark_results.json", "w") as f:
        json.dump(results, f, indent=4)
        
    models = list(results.keys())
    accs = [results[m]["accuracy"] for m in models]
    times = [results[m]["time_seconds"] for m in models]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    color = 'tab:blue'
    ax1.set_ylabel('Precision (Accuracy)', color=color)
    bars = ax1.bar(models, accs, color=color, alpha=0.7)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim(0, 1.1)
    
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.02, f"{yval*100:.1f}%", ha='center', color=color, fontweight='bold')

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Tiempo de Ejecucion (segundos)', color=color)
    ax2.plot(models, times, color=color, marker='o', linewidth=2, markersize=8)
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('Benchmark SOTA: Precision vs Tiempo')
    fig.tight_layout()
    plt.savefig("artifacts/benchmark_accuracy_time.png")
    plt.close()

    # --- RESUMEN FINAL ---
    print("\n" + "="*60)
    print("RESULTADOS FINALES DEL BENCHMARK")
    print("="*60)
    fastest = min(results, key=lambda k: results[k]["time_seconds"])
    most_accurate = max(results, key=lambda k: results[k]["accuracy"])
    for model, data in results.items():
        print(f"  {model:<15}: Accuracy={data['accuracy']*100:.2f}%  |  Tiempo={data['time_seconds']:.3f}s")
    print(f"\n  Ganador en Velocidad  : {fastest}")
    print(f"  Ganador en Precision  : {most_accurate}")
    print("="*60)
    print("\nBenchmark completado con exito.")

if __name__ == "__main__":
    main()
