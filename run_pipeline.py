import os
import subprocess
import sys

def print_step(step_name):
    print(f"\n{'='*60}")
    print(f"🚀 {step_name}")
    print(f"{'='*60}")

def run_cmd(command):
    print(f"Ejecutando: {' '.join(command)}")
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"\n❌ ERROR: El comando ha fallado. Deteniendo pipeline.")
        sys.exit(1)
    print("✅ Paso completado con éxito.\n")

def main():
    print_step("INICIANDO NEUROSYMBOLIC PIPELINE (ATLAS DINÁMICO)")
    
    # Aseguramos que la carpeta de artefactos existe
    os.makedirs("artifacts", exist_ok=True)
    
    # PASO 1: Generación de series temporales y extracción de features (Embeddings)
    print_step("PASO 1: Integración de Atractores (Lorenz, Rössler) y Extracción")
    # Cambia los nombres si en tu experiments_archive se llaman ligeramente distinto
    run_cmd(["python", "experiments_archive/continuous_attractors.py"])
    
    # PASO 2: Proyección Latente y Cálculo de Curvatura
    print_step("PASO 2: Geometría Diferencial y Clustering")
    run_cmd(["python", "experiments_archive/continuous_geometry.py"])
    
    # PASO 3: Generación de Gráficos PCA y Geodésicas
    print_step("PASO 3: Generación de Artefactos Visuales")
    run_cmd(["python", "experiments_archive/universal_atlas_visualization.py"])
    
    # PASO 4: Congelar el conocimiento en el JSON maestro
    print_step("PASO 4: Exportando Memoria Semántica (ATLAS_INSIGHTS)")
    run_cmd(["python", "export_knowledge.py"])
    
    print_step("🎉 PIPELINE COMPLETADO. Revisa la carpeta 'artifacts/'.")

if __name__ == "__main__":
    main()