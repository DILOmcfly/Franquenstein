# Respuesta a `auditoria_aprendizaje_real.md`
**Fecha:** 2026-02-25 21:22  
**Autor:** Dr. OpenClaw

## Resumen honesto
La auditoría es correcta en el diagnóstico de fondo: **la inteligencia conversacional estaba sobre-apoyada en el LLM** y el sistema de patrones no estaba aportando lo que debía en modo offline.

Además, encontré una causa técnica concreta que agravaba el problema:

- Sí se estaban guardando `response_pattern`, pero `get_best_response()` devolvía `None` en muchos casos por la lógica de selección (priorizaba score puro y no estabilidad por repeticiones).
- Por empates/floats, respuestas de count=1 quedaban arriba y bloqueaban respuestas estables count>=2.

## Evidencia (estado previo)
- `response_pattern` reportados por auditoría: 0 en ese corte.
- En revisión posterior: había patrones, pero no se recuperaban bien para `suggest_response()` por criterio de selección.

## Acciones ejecutadas YA (antes de nuevas features)

### 1) Corrección del motor de patrones
Archivo: `franquenstein/learning/patterns.py`

- En `observe_response()`:
  - ordenación cambiada a `score + count` (prioriza respuestas estables).
- En `get_best_response()`:
  - ahora selecciona primero respuestas con `score>0` y `count>=2`.
  - fallback opcional para single-shot solo si score muy alto (`>=0.9`).

### 2) Validación técnica
- Suite completa: **13/13 passing**.
- Verificación funcional:
  - `suggest_response('¿qué es python?')` => ahora devuelve respuesta aprendida.
  - Con LLM apagado (`is_available=False`), `interact('¿Qué es Python?')` responde con patrón aprendido, no con vacío.

## Conclusión técnica (pregunta clave del equipo)

### ¿Es viable aprender a responder sin depender 100% del LLM?
**Sí, es viable.**

El diseño puede y debe ser híbrido:
1. **Patrones aprendidos (offline-first)** para preguntas repetidas y conocidas.
2. **LLM** para generalización y casos nuevos.
3. **Fallback semántico/episódico** como red de seguridad.

## Plan de resolución (priorizado)

## Fase A — Inmediata (hoy)
1. ✅ Fix de selección de patrones (hecho).
2. ✅ Validación offline con ejemplos conocidos (hecho).
3. ⏳ Ejecutar mini-curriculum real supervisado para poblar `response_pattern` con QA de valor.

## Fase B — Corto plazo (siguiente bloque)
1. Añadir modo `teach_pair(question, ideal_answer, score, repeats)` para entrenamiento explícito y trazable.
2. Añadir `source='training'|'user'|'curiosity'|'test'` en episodios para filtrar calidad de aprendizaje.
3. Test nuevo obligatorio: `test_offline_response_patterns` (LLM off, respuestas correctas en preguntas enseñadas).

## Fase C — Operativa continua
1. Curriculum real (Q/A útiles, no samples genéricos).
2. Repetición espaciada sobre preguntas clave.
3. Report semanal de ratio:
   - `% respuestas resueltas por patrones`
   - `% respuestas que requirieron LLM`
   - `% fallback semántico/episódico`

## Riesgos y mitigación
- Riesgo: sobreajuste a respuestas rígidas.
  - Mitigación: usar patrones solo en inputs repetidos + LLM para variaciones.
- Riesgo: ruido por training sintético.
  - Mitigación: curriculum curado + trazabilidad por `source`.

## Cierre
La crítica del equipo está bien enfocada y la comparto. Ya está aplicada la corrección clave del retrieval de patrones y validado el comportamiento offline en preguntas enseñadas. No avanzo nuevas features de producto hasta cerrar el bloque de aprendizaje real supervisado y su test offline dedicado.
