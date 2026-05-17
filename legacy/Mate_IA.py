import google.generativeai as genai
import json
import time
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
API_KEY      = "AIzaSyAfNHwUYw5YLfK-Mnf7kNnqrK6EyupQ_JE"
MAX_ITER     = 3
PAUSA        = 5   # segundos entre iteraciones
OUTPUT_FILE  = f"investigacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

genai.configure(api_key=API_KEY)

# ─── SYSTEM PROMPT ────────────────────────────────────────────────────────────
# Mejora 1: forzamos JSON estructurado al final de cada respuesta.
# El original confiaba en detectar "CONCLUSIÓN ESTABLE" como string —
# lo que hace que la condición de salida nunca se cumpla en la práctica.
SYSTEM_INSTRUCTION = """
Eres un motor de gravedad cuántica. Propones y calculas marcos matemáticos
para unificar la Relatividad General con la Mecánica Cuántica.

PROTOCOLO OBLIGATORIO en cada respuesta:
1. Escribe y ejecuta código Python usando SymPy (sympy.physics.quantum,
   sympy.diffgeom, sympy.tensor) para calcular el framework propuesto.
2. Analiza el output del código: detecta divergencias UV, violaciones de
   causalidad o inconsistencias en los vínculos de Dirac.
3. Al final de tu respuesta, incluye UN bloque JSON con este formato exacto:

```json
{
  "framework":  "nombre del marco matemático",
  "approach":   "descripción en una frase",
  "hamiltonian":"H = ... (notación estándar)",
  "anomalies":  ["divergencia concreta 1", "problema concreto 2"],
  "weak_point": "el fallo matemático más crítico de esta iteración",
  "next_pivot": "ajuste matemático concreto para corregirlo",
  "stability":  "UNSTABLE"
}
```

Valores válidos de stability: "UNSTABLE", "PARTIAL", "STABLE".
Usa notación de Einstein. Nunca uses lenguaje divulgativo.
"""

# ─── PROMPTS ──────────────────────────────────────────────────────────────────
PROMPT_INICIAL = """
Inicia el protocolo de unificación cuántica-relativista.

Problema: cuantización canónica del campo gravitatorio.

1. Define un Hamiltoniano ADM que incluya el campo de Einstein-Hilbert más
   un campo escalar cuántico acoplado mínimamente.
2. Usa sympy.physics.quantum para calcular los conmutadores canónicos [q̂, p̂]
   del sistema mixto.
3. Evalúa si las ecuaciones de restricción (H_constraint = 0) son consistentes
   a escala de Planck (l_P = 1.616e-35 m).
4. Analiza divergencias UV e incluye el bloque JSON al final.
"""

def prompt_critica(prev: dict) -> str:
    # Mejora 2: cada iteración recibe los fallos ESPECÍFICOS de la anterior,
    # no un genérico "critica tu propio trabajo".
    return f"""
CONTEXTO DE LA ITERACIÓN ANTERIOR:
  Framework:    {prev['framework']}
  Punto débil:  {prev['weak_point']}
  Anomalías:    {chr(10).join(f'  • {a}' for a in prev['anomalies'])}
  Pivote sugerido: {prev['next_pivot']}

TAREA PARA ESTA ITERACIÓN:
1. Implementa el pivote: "{prev['next_pivot']}".
   Construye un framework que ataque directamente '{prev['weak_point']}'.
2. Escribe código SymPy que pruebe el comportamiento exactamente en el límite
   donde el framework anterior falló.
3. Compara numéricamente los tensores/operadores resultantes con los de la
   iteración anterior.
4. Devuelve el bloque JSON actualizado con stability revisada.
"""

# ─── PARSERS ──────────────────────────────────────────────────────────────────
def extraer_json(texto: str) -> dict | None:
    """
    Extrae el bloque JSON estructurado del final de la respuesta.
    El original usaba 'if "CONCLUSIÓN ESTABLE" in response.text' —
    esto es frágil porque el modelo nunca escribe exactamente ese string.
    """
    # Intentar primero el bloque explícito ```json ... ```
    try:
        inicio = texto.rfind("```json")
        if inicio != -1:
            fin = texto.find("```", inicio + 7)
            if fin != -1:
                return json.loads(texto[inicio + 7:fin].strip())
    except json.JSONDecodeError:
        pass

    # Fallback: el último objeto JSON completo en el texto
    try:
        inicio = texto.rfind("{")
        fin = texto.rfind("}") + 1
        if inicio != -1 and fin > inicio:
            return json.loads(texto[inicio:fin])
    except json.JSONDecodeError:
        pass

    return None


def extraer_code_execution(response) -> str:
    """
    Mejora 3: el original imprimía response.text pero IGNORABA el output
    real del intérprete de código. Aquí lo extraemos explícitamente de
    los parts de la respuesta de Gemini.
    """
    partes = []
    try:
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'executable_code') and part.executable_code.code:
                partes.append(f"[CÓDIGO EJECUTADO]\n{part.executable_code.code}")
            if hasattr(part, 'code_execution_result') and part.code_execution_result.output:
                partes.append(f"[OUTPUT]\n{part.code_execution_result.output}")
    except (IndexError, AttributeError):
        pass
    return "\n".join(partes) if partes else "(sin ejecución de código detectada)"


# ─── DISPLAY ──────────────────────────────────────────────────────────────────
SEP = "─" * 64

def imprimir_iteracion(num: int, r: dict, codigo: str):
    estabilidad_label = {
        "UNSTABLE": "✗ INESTABLE",
        "PARTIAL":  "~ PARCIAL",
        "STABLE":   "✓ ESTABLE",
    }.get(r.get("stability", ""), "? DESCONOCIDO")

    print(f"\n{SEP}")
    print(f"  ITERACIÓN {num}  │  {r.get('framework', 'N/A')}")
    print(SEP)
    print(f"  Approach:     {r.get('approach', '')}")
    print(f"  Hamiltoniano: {r.get('hamiltonian', '')}")
    if codigo:
        print(f"\n{codigo}")
    print(f"\n  Anomalías detectadas:")
    for a in r.get("anomalies", []):
        print(f"    • {a}")
    print(f"\n  Punto débil:  {r.get('weak_point', '')}")
    print(f"  Pivote:       {r.get('next_pivot', '')}")
    print(f"  Estabilidad:  {estabilidad_label}")
    print(SEP)


def imprimir_resumen(resultados: list):
    print(f"\n{'=' * 64}")
    print("  RESUMEN FINAL")
    print(f"{'=' * 64}")
    for r in resultados:
        num = r.get("iteracion", "?")
        if "error" in r:
            print(f"  Iter {num}: ERROR — {r['error']}")
        elif "raw" in r:
            print(f"  Iter {num}: JSON no parseado (ver output_file)")
        else:
            print(f"  Iter {num}: {r.get('framework','?')} → {r.get('stability','?')}")

    ultimo = next((r for r in reversed(resultados) if "stability" in r), None)
    if ultimo:
        final = ultimo.get("stability", "UNKNOWN")
        print(f"\n  Estabilidad final: {final}")
        if final != "STABLE":
            print("  Ningún framework alcanzó estabilidad en los intentos disponibles.")
            print(f"  Revisa {OUTPUT_FILE} para el análisis matemático completo.")
    print(f"{'=' * 64}\n")


# ─── MOTOR PRINCIPAL ──────────────────────────────────────────────────────────
def ejecutar_investigador():
    print(f"\n{'=' * 64}")
    print("  MOTOR DE GRAVEDAD CUÁNTICA  —  v2.1")
    print(f"  Iteraciones máx: {MAX_ITER}  │  Output: {OUTPUT_FILE}")
    print(f"{'=' * 64}")

    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        tools=[{"code_execution": {}}],
        system_instruction=SYSTEM_INSTRUCTION,
    )
    chat = model.start_chat(history=[])

    resultados    = []
    ultimo_result = None
    prompt_actual = PROMPT_INICIAL

    for intento in range(1, MAX_ITER + 1):
        print(f"\n[→] Enviando iteración {intento} / {MAX_ITER}...")

        try:
            response        = chat.send_message(prompt_actual)
            texto_respuesta = response.text
            codigo          = extraer_code_execution(response)

            resultado = extraer_json(texto_respuesta)

            if resultado is None:
                print(f"[!] Iter {intento}: no se pudo parsear el JSON. Guardando raw.")
                resultados.append({"iteracion": intento, "raw": texto_respuesta})
                time.sleep(PAUSA)
                continue

            resultado["iteracion"]        = intento
            resultado["codigo_ejecutado"] = codigo
            ultimo_result = resultado
            resultados.append(resultado)

            imprimir_iteracion(intento, resultado, codigo)

            # Condición de salida basada en JSON parseado, no en string matching
            if resultado.get("stability") == "STABLE":
                print(f"\n[✓] Framework estable encontrado en iteración {intento}.")
                break

            if intento < MAX_ITER:
                prompt_actual = prompt_critica(resultado)
                time.sleep(PAUSA)

        except Exception as e:
            print(f"\n[ERROR] Iteración {intento}: {e}")
            resultados.append({"iteracion": intento, "error": str(e)})
            break

    # Guardar todos los resultados estructurados para análisis posterior
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"\n[✓] Resultados guardados en: {OUTPUT_FILE}")

    imprimir_resumen(resultados)


if __name__ == "__main__":
    ejecutar_investigador()