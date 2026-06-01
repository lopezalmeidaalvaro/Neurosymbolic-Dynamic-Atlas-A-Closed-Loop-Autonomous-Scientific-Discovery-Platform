# Search Space Audit Report

This report presents a rigorous audit of the symbolic search space of **HypoGen** (**Fase 1 – Auditoría del Espacio de Búsqueda**). We generated **10,000 independent mathematical hypotheses** using the current configuration of `HypothesisGenerator` to analyze coverage, grammar entropy, depth metrics, and structural bias.

---

## 📊 1. Cobertura de Familias Funcionales (N = 10,000)

| Familia Funcional | Porcentaje de Generación | Cantidad de Hipótesis | Descripción / Filtros |
| :--- | :--- | :--- | :--- |
| **exponential** | 17.11% | 1,711 | Contiene la función exponencial `exp(...)` |
| **tanh** | 16.81% | 1,681 | Contiene la función tangente hiperbólica `tanh(...)` |
| **rational** | 25.64% | 2,564 | Contiene divisiones `/` con la variable `r` en el denominador |
| **polynomial** | 38.49% | 3,849 | Solo contiene constantes, variable `r` y operadores simples (`+`, `-`, `*`) |
| **power_law** | 1.95% | 195 | Contiene expresiones de potencia negativa o fraccionaria (ej. `pow(r, -n)`) |
| **sigmoid** | 0.00% | 0 | Contiene la función sigmoide (no definida en la gramática actual) |
| **mixed** | 0.00% | 0 | Combinación de múltiples familias trascendentes en una sola hipótesis |

> [!IMPORTANT]
> Las familias **polynomial** (38.49%) y **rational** (25.64%) dominan la gramática base, mientras que la generación de **power_law** es extremadamente baja (1.95%) y la presencia de sigmoides o expresiones mixtas es nula (0%). Esto explica de forma concluyente la rigidez y el colapso exploratorio de familias observado en las fases previas.

---

## 🔑 2. Entropía de la Gramática

La entropía de la gramática libre de contexto (CFG) se calculó como la suma de las entropías de selección de reglas para cada no terminal $A$:
$$H(A) = - \sum_{i=1}^{k_A} \frac{1}{k_A} \log_2 \left(\frac{1}{k_A}\right) = \log_2 k_A$$

* **Expr** ($k = 3$ producciones) $\rightarrow$ `1.5850` bits
* **Term** ($k = 3$ producciones) $\rightarrow$ `1.5850` bits
* **Factor** ($k = 6$ producciones) $\rightarrow$ `2.5850` bits
* **Const** ($k = 6$ producciones) $\rightarrow$ `2.5850` bits
* **Var** ($k = 1$ producción) $\rightarrow$ `0.0000` bits

### **Total Theoretical Grammar Entropy**: `8.3399` bits

---

## 📏 3. Profundidad Efectiva y Longitud Simbólica

* **Profundidad Media**: `4.00`
* **Profundidad Máxima**: `4`
* **Longitud Simbólica Media**: `8.78` nodos por expresión

---

## 🔍 4. Análisis de Sesgo (Bias Analysis)

### **¿Existe sesgo estructural hacia exponenciales?**
**No de forma mayoritaria en la gramática pura.** La proporción de términos puramente exponenciales generados por el CFG es de **17.11%**, lo cual es comparable a la de tanh (**16.81%**). 
Sin embargo, sí existe un sesgo masivo y dominante hacia expresiones polinómicas simples y funciones elementales racionales, debido al bajo valor de `max_depth` (3 en la llamada recursiva interna) que causa que el generador fuerce la terminación hacia constantes y variables rápidamente para evitar desbordamiento. Esto restringe severamente la capacidad del sistema para proponer ansatzes alternativos complejos y variados de manera natural.
