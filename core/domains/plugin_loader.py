import os
import sys
import importlib

def discover_domains():
    """
    Busca y carga dinámicamente archivos plugin.py en physics, satellite (o satelite) y quantum.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Asegurar que el directorio raíz está en sys.path para poder realizar las importaciones
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    discovered = []
    # Lista de carpetas de dominio candidatas
    domains = ["physics", "satellite", "satelite", "quantum"]
    
    for domain in domains:
        plugin_path = os.path.join(base_dir, domain, "plugin.py")
        if os.path.exists(plugin_path):
            module_name = f"{domain}.plugin"
            try:
                # Recargar si ya existe en sys.modules para evitar problemas en tests
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                else:
                    importlib.import_module(module_name)
                discovered.append(domain)
            except Exception as e:
                print(f"[WARNING] PluginLoader: Error cargando {module_name}: {e}")
                
    return discovered
