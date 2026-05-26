# Diseño de Experimento: Falsación de Conjetura 2

## Hipótesis Original
**Los sistemas logistic_map, logistic_sweep pertenecen a la misma clase de universalidad topológica debido a su proximidad geométrica densa.**

**Confianza Inicial:** 0.6782

## Instrucciones de Falsación (Prompt Sugerido)
> **Ejecuta lo siguiente para intentar romper esta conjetura:**
> 1. Introduce ruido estocástico (e.g., ruido Gaussiano $\sigma=0.1$) en las ecuaciones de estos sistemas y recalcula el embedding estructural.
> 2. Realiza un barrido paramétrico extremo fuera del régimen actual para forzar transiciones de fase desconocidas.
> 3. Verifica si la correlación o el clúster se disuelven (si la distancia coseno cae drásticamente o la correlación baja de 0.8).

## Evidencia Actual
```json
{
  "silhouette_score": 0.6782184978829708,
  "cluster_size": 151,
  "cluster_variance": 0.7172870872756156
}
```
