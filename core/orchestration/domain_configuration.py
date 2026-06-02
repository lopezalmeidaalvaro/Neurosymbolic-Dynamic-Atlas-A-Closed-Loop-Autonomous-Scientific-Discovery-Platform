import os
import yaml

class DomainConfiguration:
    """
    Carga configuraciones de dominios científicos (datasets, métodos, prompts y restricciones)
    desde archivos YAML para desacoplar el orquestador principal.
    """
    def __init__(self, domain_name="physics"):
        self.domain_name = domain_name
        self.datasets = []
        self.methods = []
        self.prompts = {}
        self.constraints = {}
        self.load()

    def load(self):
        # Intentar cargar desde el directorio raíz configs/domains/
        # Para test_dependency_injection o ejecución relativa, buscamos el path correcto
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        yaml_path = os.path.join(base_dir, "configs", "domains", f"{self.domain_name}.yaml")
        
        # Fallback local o de debug
        if not os.path.exists(yaml_path):
            yaml_path = os.path.join("configs", "domains", f"{self.domain_name}.yaml")

        if os.path.exists(yaml_path):
            try:
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data:
                        self.datasets = data.get("datasets", [])
                        self.methods = data.get("methods", [])
                        self.prompts = data.get("prompts", {})
                        self.constraints = data.get("constraints", {})
            except Exception as e:
                print(f"[WARNING] DomainConfiguration: Error al cargar {yaml_path}: {e}")
        else:
            # Fallback hardcodeado de seguridad en caso de que no se encuentre el archivo
            if self.domain_name == "physics":
                self.datasets = [
                    "synthetic_lorenz (Lorenz 3D chaotic attractor timeseries)",
                    "synthetic_rossler (Rossler attractor timeseries)",
                    "ecg_data (Arrhythmic and normal sinus rhythm electrocardiogram records)",
                    "ucr_datasets (Standard benchmarks for time series classification)",
                ]
                self.methods = [
                    "topological (Takens phase space reconstruction, persistent homology Betti-0/1 curves)",
                    "geometric (Ollivier-Ricci graph curvature, Laplace-Beltrami spectral mapping, diffusion maps)",
                    "koopman (Dynamic Mode Decomposition, Koopman operator spectral eigenvalues)",
                    "symbolic (SINDy and PySR equations discovery, sparse regression)",
                ]
                self.prompts = {
                    "observations": "Dynamic chaos and nonlinear behaviors under different noise regimes."
                }
                self.constraints = {
                    "allowed_singularities": False
                }
