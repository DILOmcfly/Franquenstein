# Análisis de Calidad Neural (H2)
**Fecha:** 2026-02-26 00:52

## Objetivo
Evaluar calidad semántica de respuestas neurales tras entrenamiento conversacional profundo.

## Dataset evaluado
- Re-ejecución: `train_phase3_test.py`
- Preguntas: 30
- Resultado bruto:
  - Neural: 29
  - LLM: 0
  - Fallback: 1

## Métrica rápida aplicada
Se aplicó una heurística de “ruido semántico” sobre muestras, marcando respuestas con tokens plantillados o conectores débiles recurrentes (`paso`, `gusta`, `sobre`, etc.).

- Total evaluadas: 30
- Marcadas como bajo valor por heurística estricta: 21
- **Coherencia semántica estimada (heurística estricta): 30%**

> Nota: esta métrica penaliza fuerte y tiene falsos positivos; se usa como señal de mejora, no como verdad absoluta.

## Hallazgos
1. **Cobertura neural excelente** (29/30), pero calidad semántica irregular.
2. Persisten patrones de verbalización plantillada (“Me gusta esta conexión...”, “Sobre X...”), incluso cuando el fondo conceptual es válido.
3. Tokens residuales de poco valor siguen contaminando algunas respuestas de alto nivel.

## Acciones recomendadas inmediatas
1. Subir filtro de calidad en `ResponseWeaver`:
   - descartar respuestas con <2 conceptos significativos.
   - forzar reformulación cuando detecte conectores vacíos.
2. Añadir métrica automática en tests:
   - `% respuestas con 2+ conceptos semánticos válidos`
   - `% respuestas con token ruido`
3. Continuar TRAIN profundo por dominios débiles detectados.

## Conclusión
Franquenstein ya **piensa con su grafo** (dominancia neural), pero el siguiente cuello de botella es **calidad lingüística y limpieza semántica de salida**.

Esto es una buena noticia: la arquitectura cognitiva está viva; ahora toca refinar expresión y precisión.
