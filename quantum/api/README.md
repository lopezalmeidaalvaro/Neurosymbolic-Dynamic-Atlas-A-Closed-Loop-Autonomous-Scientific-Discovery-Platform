# QADE API REST v0.2 — MVP

Módulo REST API mínimo que permite compilar circuitos cuánticos usando la optimización QADE, protegido con autenticación por API Key.

## Instalación

1. Asegúrate de tener las dependencias del core de QADE y las de la API instaladas:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements_api.txt
   ```

## Authentication

Todas las rutas excepto `/health` requieren el siguiente header HTTP:
`X-API-Key: <tu_api_key>`

### Configurar la API Key para desarrollo local
Define la variable de entorno `QADE_API_KEY` antes de arrancar el servidor:
```bash
# En PowerShell
$env:QADE_API_KEY="mi-clave-secreta-local"

# En Linux / macOS / Bash
export QADE_API_KEY="mi-clave-secreta-local"
```
*(Nota: Si no se define esta variable, el servidor generará una clave aleatoria (UUID) en runtime para esta sesión y la mostrará en los logs para que puedas utilizarla. Nunca se hardcodea en el código).*

## Cómo arrancar el servidor

Arranca el servidor local de desarrollo usando Uvicorn:
```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

El servidor estará disponible en [http://127.0.0.1:8000](http://127.0.0.1:8000). Puedes consultar la documentación interactiva de la API (Swagger UI) en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Ejemplos de uso con `curl`

### 1. Health check (`GET /health`)
*Ruta pública (no requiere autenticación)*
```bash
curl -X GET http://127.0.0.1:8000/health
```
**Respuesta esperada:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "backend": "ibm_fez"
}
```

### 2. Obtener backends disponibles (`GET /backends`)
*Requiere header X-API-Key*
```bash
curl -X GET http://127.0.0.1:8000/backends \
     -H "X-API-Key: mi-clave-secreta-local"
```
**Respuesta esperada:**
```json
{
  "available": ["ibm_fez", "fake_fez", "fake_sherbrooke"]
}
```

### 3. Compilar circuito cuántico (`POST /compile`)
*Requiere header X-API-Key*

#### Compilación usando el backend local `fake_fez` (no requiere credenciales IBM):
```bash
curl -X POST http://127.0.0.1:8000/compile \
     -H "X-API-Key: mi-clave-secreta-local" \
     -H "Content-Type: application/json" \
     -d '{
       "circuit_qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[5];\nh q[0];\ncx q[0],q[1];\ncx q[1],q[2];\ncx q[2],q[3];\ncx q[3],q[4];",
       "backend_name": "fake_fez",
       "optimization_level": 1,
       "hardware_aware": true
     }'
```

#### Compilación usando el backend real `ibm_fez` (requiere `IBMQ_API_KEY` en la variable de entorno):
1. Exporta tu clave de la API de IBM:
   ```bash
   # En PowerShell
   $env:IBMQ_API_KEY="TU_CLAVE_API_AQUÍ"
   
   # En Linux / macOS / Bash
   export IBMQ_API_KEY="TU_CLAVE_API_AQUÍ"
   ```
2. Realiza la petición curl:
   ```bash
   curl -X POST http://127.0.0.1:8000/compile \
        -H "X-API-Key: mi-clave-secreta-local" \
        -H "Content-Type: application/json" \
        -d '{
          "circuit_qasm": "OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[5];\nh q[0];\ncx q[0],q[1];\ncx q[1],q[2];\ncx q[2],q[3];\ncx q[3],q[4];",
          "backend_name": "ibm_fez",
          "optimization_level": 1,
          "hardware_aware": true
        }'
   ```

**Respuesta esperada:**
```json
{
  "compiled_qasm": "OPENQASM 2.0; ...",
  "gate_count": {
    "total": 12,
    "one_qubit": 6,
    "two_qubit": 6
  },
  "depth": 8,
  "qubits_selected": [1, 2, 3, 4, 5],
  "compile_time_ms": 142.35,
  "qade_version": "0.1.0",
  "note": null
}
```

## Ejecución de Tests

Ejecuta la suite de pruebas unitarias/integración de la API:
```bash
pytest api/test_api.py
```
