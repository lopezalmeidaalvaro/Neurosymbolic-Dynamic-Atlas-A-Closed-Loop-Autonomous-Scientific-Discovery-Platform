# PLACEMENT_VERIFICATION

## 1. ¿Stage C implementa placement real diferente al trivial?
**NO** (para el circuito `GHZ_5q` en `FakeFez`).

Aunque el código de `QubitPlacement.place(method="fidelity_aware")` contiene la lógica y algoritmos de asignación basados en fidelidad, en la práctica retorna exactamente el mapeo trivial `{0: 0, 1: 1, 2: 2, 3: 3, 4: 4}` para `GHZ_5q` sobre `FakeFez`. Por lo tanto, el conjunto de qubits físicos seleccionados y su correspondencia lógica-física es idéntica al layout trivial.

## 2. Si SÍ: qué qubits selecciona para GHZ_5q en FakeFez y por qué son mejores
*(N/A - La respuesta es NO. Véase la explicación a continuación).*

## 3. Si NO: descripción del bug y fix mínimo
### Diagnóstico del comportamiento (¿Por qué ocurre esto?)
El algoritmo de `fidelity_aware_placement` opera de la siguiente manera:
1. **Puntuación de Qubits**: Calcula una puntuación de calidad para cada qubit físico basada en $T_1, T_2$, error de lectura y promedio de errores de compuertas 2Q.
2. **Qubit Inicial (Ancla)**: El qubit físico con la puntuación más alta del backend se selecciona como ancla para el primer qubit lógico más activo. En `FakeFez`, el qubit físico con la puntuación más alta es el **Qubit 1** (puntuación: `0.6939`, $T_1 = 255.7\text{ us}$, $T_2 = 302.8\text{ us}$).
3. **Crecimiento Codicioso**: Para los siguientes qubits, la función de coste está dominada por la distancia física en el acoplamiento (`distance_cost`), que penaliza fuertemente colocar qubits no adyacentes. Esto obliga a colocar los qubits lógicos restantes de forma contigua a los ya colocados.
4. **Mapeo Resultante**: Comenzando en el qubit `1`, las únicas opciones adyacentes disponibles en la topología lineal para completar los 5 qubits son `0` y `2`, extendiéndose luego a `3` y `4`. Esto resulta en el layout exacto `{1: 1, 2: 2, 3: 3, 0: 0, 4: 4}`, que equivale al trivial.

### El "Greedy Local Minimum" Trap (Trampa del Mínimo Local)
Al forzar el inicio en el qubit de mayor puntuación absoluta (`1`), el algoritmo se ve obligado a utilizar su vecino adyacente **Qubit 0**, el cual tiene una calidad extremadamente pobre ($T_1 = 48.8\text{ us}$, $T_2 = 42.4\text{ us}$, readout error = $1.15\%$). Esto reduce drásticamente la fidelidad teórica estimada del layout a **0.866524**.

Si el algoritmo hubiera evitado empezar en el qubit "estrella" `1` y hubiese buscado un subgrafo lineal de 5 qubits con mejor calidad global (por ejemplo, `[2, 3, 4, 5, 6]`), habría alcanzado una fidelidad teórica estimada de **0.882135** (una mejora de **+1.56%** en fidelidad).

### Fix Mínimo Sugerido (Heurística de Subgrafos / Paths)
Para circuitos lineales pequeños como GHZ o QFT, en lugar de un crecimiento qubit a qubit codicioso que cae en mínimos locales:
1. Identificar todos los subgrafos o caminos de longitud $N$ (en este caso 5) en el mapa de acoplamiento.
2. Evaluar la calidad media o la fidelidad estimada de cada camino completo.
3. Seleccionar el camino con la fidelidad teórica más alta como el layout inicial.

## 4. Implicación para el claim ante inversores
**Claim pendiente de implementación — NO incluir en email a Quantonation hasta corregir.**

Aunque QADE obtuvo un win rate de 60% (3/5) en el Run 6 sobre `ibm_fez` real frente a Qiskit L3, esta mejora en fidelidad (+0.82% en `GHZ_5q`) se debió a optimizaciones en la etapa de síntesis de puertas y reducción de profundidad, y **no** a una colocación inteligente (placement) de qubits, ya que el compilador terminó usando el layout trivial `[0,1,2,3,4]`. El claim de que QADE optimiza la fidelidad mediante un posicionamiento inteligente consciente de la calibración real del hardware está pendiente de una implementación robusta que resuelva la trampa del mínimo local codicioso.
