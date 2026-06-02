# FASE 2 — Auditoría de Evolución Dinámica de Colapso

En esta segunda fase, auditamos los resultados de la resolución numérica de las ecuaciones diferenciales efectivas que gobiernan la evolución relativista dinámica del colapso de la nube.

---

## Resultados del Solucionador ODE del Colapso

Integramos numéricamente la ecuación diferencial del factor de escala $a(t)$ con espaciado de tiempo adaptable de Runge-Kutta de cuarto orden, obteniendo los siguientes perfiles de evolución temporal para el factor de escala $a(t)$ y la densidad clásica de materia $\rho(t)$:

- **Etapa de Colapso ($t \in [0, 9.38]$):**
  - El factor de escala $a(t)$ decrece suavemente desde $a(0) = 1.0$, acelerando el colapso gravitatorio conforme la atracción gravitatoria se intensifica.
  - La densidad clásica $\rho(t) = 0.08 / a^3$ aumenta de forma correspondiente, pasando de $\rho(0) = 0.08$ a $\rho(t_{bounce}) = 8.0$ Planck.
- **Punto del Rebote Cuántico ($t_{bounce} \approx 9.38$ Planck):**
  - La velocidad de colapso $\dot{a}$ cae exactamente a cero.
  - El factor de escala alcanza su **mínimo valor absoluto**:
    $$a_{min} \approx 0.2154 \text{ Planck}$$
  - La densidad de materia física real alcanza su **máximo valor absoluto**:
    $$\rho_{max} = \rho(a_{min}) = \rho_{crit} = 8.0 \text{ Planck}$$
- **Etapa de Expansión/Rebote ($t > 9.38$):**
  - El factor de escala $a(t)$ rebota simétricamente y comienza a expandirse de nuevo, regresando a la planitud plana a tiempos tardíos. La densidad de materia decrece rápidamente.

Esta evolución acoplada del factor de escala y de la densidad física se detalla gráficamente en la simulación:
![Evolución del Colapso](/figures/collapse_evolution.png)

Como se ilustra en `figures/collapse_evolution.png`:
- El factor de escala (curva azul) exhibe una trayectoria en forma de "U" perfectamente suave, con su mínimo en $a_{min} \approx 0.215$ en el centro de la simulación.
- La densidad clásica de materia (curva marrón discontinua) crece de forma exponencial durante el colapso, alcanzando su pico de $8.0$ en el punto exacto de rebote, y disminuye de forma simétrica tras la expansión.

---

## Verificación de Curvatura Finito

En el colapso clásico de Oppenheimer-Snyder, el factor de escala colapsa a cero ($a \to 0$), lo que provoca que la curvatura del espaciotiempo diverja a infinito, creando una singularidad central física.

En nuestro modelo cuántico de bucles regularizado:
- El Kretschmann escalar se acopla a la densidad de energía efectiva $\rho_{eff}$:
  $$K(t) = 12 \rho_{eff}(t)^2$$
- Dado que la densidad efectiva está acotada por la regularización ($\rho_{eff}(t) \leq \rho_{crit}/2 = 4.0$ Planck):
  $$K_{max} = 12 \times (4.0)^2 = 192.0 \text{ (Planck)}$$
- **Conclusión de Finitud:** El invariante de Kretschmann permanece estrictamente **finito y acotado** a lo largo de toda la evolución, alcanzando un valor pico de solo $192.0$ unidades de Planck en el rebote, demostrando de forma contundente que **la singularidad física de curvatura clásica queda completamente resuelta dinámicamente**.
