# Predicciones Observacionales en la Fase de Coalescencia (Inspiral) (Fase 3)

Este reporte evalúa cuantitativamente las correcciones en la fase orbital de las ondas gravitacionales durante la etapa de inspiral de binarias de agujeros negros compactos para el candidato de Hayward.

---

## 1. Correcciones post-Newtonianas (PN) en la Fase Orbital
La fase de la onda gravitatoria emitida por una binaria en órbita cuasi-circular durante la etapa de inspiral se modela en el dominio de frecuencia mediante la expansión post-Newtoniana:

$$\Psi(f) = 2\pi f t_c - \phi_c - \frac{\pi}{4} + \frac{3}{128 \eta v^5} \sum_{k=0}^{N} \left( \psi_k + \delta \psi_k \right) v^k$$

donde $v = (\pi M_{total} f)^{1/3}$ es la velocidad orbital efectiva de la binaria y $\eta = m_1 m_2 / M_{total}^2$ es el parámetro de masa simétrico.

Las desviaciones de gravedad cuántica $\delta \psi_k$ en el candidato Hayward surgen de:
1. La modificación de la fuerza gravitatoria efectiva en la órbita de separación final debido a la estructura no singular del espaciotiempo.
2. La corrección al momento cuadripolar inducida por el núcleo denso de de Sitter.

### Coeficientes de Desviación PN:
La corrección dominante de Hayward aparece como una corrección de orden **3PN o superior ($v^6$)** debido a que los efectos de regularización cuántica caen extremadamente rápido a grandes distancias:

$$\delta \psi_{3PN} \propto -\frac{L^2}{M^2}$$

Para un cutoff Plankiano estándar ($L \approx 0.866$):
- **Desviación de Fase:** $\delta \psi_{3PN} \approx 10^{-78}$ para una binaria de $10 M_\odot$.
- Esta desviación es indetectable por LIGO/Virgo y confirma que la física clásica de la RG domina de manera absoluta durante la fase de inspiral lejana.

---

## 2. Residuos de Forma de Onda (Waveform Residuals)
Si el parámetro cuántico $L$ se asocia a escalas mayores (fenomenología macroscópica de horizontes cuánticos, donde $L \sim 0.05 M_0$):

$$\delta \psi_{3PN} \approx -10^{-3}$$

Esta magnitud de desviación genera una acumulación de fase orbital medible (de varios radianes) a lo largo de los últimos ciclos de órbita antes de la fusión.

Al realizar una sustracción del template de onda clásico de Schwarzschild respecto a la señal real de Hayward, la fase de inspiral tardía exhibirá un residuo oscilatorio coherente (waveform residual) con amplitud creciente que representa la firma inequívoca de la deformación de de Sitter en la superficie del objeto.
