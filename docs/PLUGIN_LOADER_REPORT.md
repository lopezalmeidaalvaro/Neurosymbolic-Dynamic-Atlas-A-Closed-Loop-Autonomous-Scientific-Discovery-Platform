# Reporte de Plugin Loader (Fase 0E.7)

Este informe detalla el mecanismo de autodescubrimiento y carga dinámica de plugins en `Neurosymbolic-Dynamic-Atlas`.

---

## 1. Mecánica de Autodescubrimiento

El cargador de plugins está implementado en [plugin_loader.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/core/domains/plugin_loader.py).

Cuando la factoría de científicos es importada o solicitada (`create_scientist(domain_name)`), invoca de forma automática al método `discover_domains()`.

Este método:
1. Obtiene la ruta del directorio raíz del proyecto de forma dinámica.
2. Comprueba la existencia física de las carpetas de dominio (`physics/`, `satellite/`, `satelite/`, `quantum/`).
3. Busca el archivo `plugin.py` en cada carpeta.
4. Si el archivo existe, realiza una importación dinámica mediante `importlib.import_module()`.
5. Si el módulo ya había sido cargado, utiliza `importlib.reload()` para asegurar que cualquier modificación en caliente o pruebas unitarias sucesivas no dejen un estado sucio en el registro global.

---

## 2. Plugins de Dominio Registrados

Hemos creado e integrado los siguientes puntos de entrada de plugin:

- **Physics Plugin ([physics/plugin.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/physics/plugin.py)):** Registra el dominio clásico de física general utilizando la factoría `create_classical_container()` y su configuración YAML.
- **Quantum Plugin ([quantum/plugin.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/quantum/plugin.py)):** Registra un stub/molde para computación cuántica, aislando el espacio de trabajo para el desarrollo futuro de circuitos hamiltonianos y mapeo simbólico.
- **Satellite Plugin ([satelite/plugin.py](file:///c:/Users/Alvaro/Desktop/ia-matematica-github/satelite/plugin.py)):** Registra un stub de telemetría de satélites y calibración de filtros de Kalman (EKF).

---

## 3. Aislamiento y Pruebas en Tiempo de Ejecución

La carga dinámica se verificó en la suite de pruebas mediante el comando `python -m pytest`:
- Los tres plugins se descubren y cargan con éxito en tiempo de ejecución, poblando automáticamente el registro.
- La ejecución de `create_scientist("physics")` recupera la especificación registrada y devuelve el orquestador correctamente instanciado con su Sandbox y LLM clásico, cumpliendo plenamente con el criterio de éxito:
  `MULTI_DOMAIN_RUNTIME = TRUE`
