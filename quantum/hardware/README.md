# QADE IBM Quantum Hardware Validation Suite

> **⚠️ DISCLOSURE:** Todos los presupuestos, costes y proyecciones de ingresos mencionados en esta documentación representan simulaciones teóricas y especulativas. QADE no ha facturado ingresos comerciales ni tiene contratos activos hasta la fecha. (modelo especulativo — sin revenue real)

Esta carpeta contiene el conjunto de herramientas para ejecutar y validar los circuitos transpilados por QADE en hardware cuántico real de IBM Quantum utilizando **Qiskit Runtime (SamplerV2)**.

---

## 1. Configuración de Cuenta de IBM Quantum

### Paso 1.1: Obtener una Cuenta y Token API
1. Regístrate en [quantum.ibm.com](https://quantum.ibm.com/).
2. Accede a **Account Settings** y copia tu token de API único.
3. Define tu variable de entorno en tu terminal (NUNCA la escribas directamente en el código):
   ```bash
   export IBM_QUANTUM_TOKEN=tu_token_aqui
   ```
   En Windows (PowerShell):
   ```powershell
   $env:IBM_QUANTUM_TOKEN="tu_token_aqui"
   ```

### Paso 1.2: Acceso Gratuito y de Pago
*   **Acceso Abierto (Open Plan)**: IBM Quantum ofrece acceso básico gratuito a sistemas de hasta 127 qubits (como `ibm_brisbane` o `ibm_kyoto`) con límites de tiempo de computación mensual gratuitos.
*   **Acceso Académico/Enterprise**: Si eres miembro de una institución asociada al IBM Quantum Network, puedes solicitar asignaciones de mayor prioridad y colas preferentes.

---

## 2. Flujo de Trabajo en Orden de Ejecución

Sigue exactamente estos pasos para realizar la validación:

### Paso 1: Autenticación y Verificación de Cuenta
Verifica la conexión con los servidores de IBM y encuentra el backend con menos congestión:
```bash
python quantum/hardware/setup_ibm_account.py
```
Este script guardará tus credenciales localmente para evitar tener que definirlas repetidamente y te recomendará un backend óptimo de $\ge 5$ qubits.

### Paso 2: Ejecución de Simulación en Modo Dry-Run (Verificación Local)
Antes de enviar trabajos reales a la cola de IBM, valida localmente que los 4 circuitos de validación se transpilas correctamente con QADE y Qiskit L3:
```bash
python quantum/hardware/qade_real_hardware_validation.py
```
*   *Nota*: El script usa un backend simulado local (`GenericBackendV2`) en modo dry-run por defecto. No requiere el token de IBM ni consume créditos.

### Paso 3: Envío de Trabajos Reales a IBM Quantum
Una vez verificado el paso de compilación local, envía los 8 trabajos a la QPU física de IBM:
```bash
python quantum/hardware/qade_real_hardware_validation.py --run
```
*   *Advertencia*: Este comando mostrará una alerta de costes y un prompt de confirmación. Tras presionar `y`, se enviarán los trabajos y se generará un archivo `benchmarks/results/hardware_real/job_ids_TIMESTAMP.json` con los identificadores únicos de los trabajos.

### Paso 4: Recuperación de Resultados de la QPU
El tiempo en la cola de IBM puede variar de minutos a horas. Puedes monitorizar el estado en [quantum.ibm.com/jobs](https://quantum.ibm.com/jobs). Una vez que todos estén completados, descarga los resultados y calcula la fidelidad de Hellinger ejecutando:
```bash
python quantum/hardware/recover_jobs.py --job-ids benchmarks/results/hardware_real/job_ids_TIMESTAMP.json
```
Esto simulará las distribuciones ideales noiseless mediante `Statevector`, las cruzará con los resultados reales obtenidos de la QPU y guardará los resultados en `hardware_results_TIMESTAMP.json`.

### Paso 5: Generación del Informe de Análisis
Genera el informe comparativo final en formato Markdown:
```bash
python quantum/hardware/analyze_hardware_results.py --results benchmarks/results/hardware_real/hardware_results_TIMESTAMP.json
```
Este script creará un archivo `report_TIMESTAMP.md` en el directorio de resultados.

---

## 3. Integración en el Dossier de Subvenciones (Grants)

Una vez completada la ejecución física en hardware real y generado el informe de análisis, sigue estos pasos para actualizar tus propuestas de subvención (por ejemplo, CDTI o EIC):

1.  **Modifica el Dossier de Subvenciones**:
    *   Abre `docs/quantum/QADE_GRANT_DOSSIER_V2.md`.
    *   Bajo la sección **WP1: Physical Hardware Validation**, reemplaza los KPIs planificados por los resultados de ejecución verificados.
    *   Mueve las métricas de fidelidad de la sección **ESTIMATED (ESTIMADO)** a la sección **MEASURED (MEDIDO)**.
2.  **Agrega Evidencias de Ejecución**:
    *   Incluye la lista de **Job IDs** reproducibles generada en el informe de análisis.
    *   Copia la tabla comparativa de fidelidades observadas en la sección de mérito técnico del dossier.
3.  **Presentación de Resultados Negativos**:
    *   Si QADE no supera a Qiskit en la QPU real, presenta el análisis de deriva de calibración (calibration drift) detallado en el informe. Esto demuestra madurez técnica y honestidad científica ante los evaluadores, justificando la necesidad de financiación adicional para continuar con el desarrollo del bucle de corrección en la Phase IX.
