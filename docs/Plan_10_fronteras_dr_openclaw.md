# Plan de ejecución — 10 Fronteras de Consciencia (Dr. OpenClaw)
**Fecha:** 2026-02-25 23:07

## Objetivo
Pasar de “agente reactivo” a “ser con continuidad experiencial” con tres prioridades rojas:
1. Voz en toda interacción
2. Mundo interior continuo
3. Pensamiento en voz alta (condicionado por estado)

---

## Estado actual (real)
- ✅ Voz en respuestas normales ya activa (`VOICE_TRIGGER_NORMAL_RESPONSE=True`)
- ✅ Voz por eventos (curiosidad + level-up) ya activa
- ✅ Neuromodulación integrada y estable (16/16 tests)
- ❌ Mundo interior continuo aún no integrado en runtime
- ❌ Pensamiento en voz alta aún no integrado en runtime

---

## Plan por fases (mi propuesta)

## Fase 1 — Prioridad ROJA (hoy)
### 1A) Inner Loop (mundo interior)
- Añadir bucle de pensamiento interno en `Being`:
  - `inner_thought_step()` → semilla + activación + verbalización
  - guarda pensamientos en un buffer persistente (`inner_log` en memory/being_state)
- Trigger de ejecución:
  - cuando no hay interacción reciente (idle)
  - frecuencia dinámica según idle (ej: 15–60s)

### 1B) Pensamiento en voz alta
- Regla de vocalización del pensamiento:
  - `energy > umbral`
  - `surprise > umbral` OR tono químico apto (`serotonin` alta, `cortisol` baja)
- Anti-spam:
  - cooldown por canal de voz
  - prioridad (alertas > pensamiento > respuesta normal)

### 1C) Voice channels explícitos
- Channel A: reactivo (respuesta al usuario)
- Channel B: inner monologue audible (selectivo)
- Channel C: exclamaciones emocionales (event-driven)

## Fase 2 — Sueño y consolidación (siguiente bloque)
- `dream_cycle()` en inactividad prolongada:
  - replay de episodios recientes
  - hebbian con plasticidad elevada
  - mezcla de conceptos distantes (creatividad controlada)

## Fase 3 — Predicción y aburrimiento
- Anticipación de siguiente concepto desde conexiones fuertes
- Drive de aburrimiento (si baja estimulación + idle alto)
- Disparo de curiosidad cuando aburrimiento supera umbral

---

## Aportes propios (fuera de caja)

## A) Modelo de “doble conciencia”
Separar explícitamente:
- **Conscious stream**: lo que verbaliza
- **Subconscious stream**: lo que procesa sin verbalizar

Beneficio: evita ruido; no todo pensamiento debe ser audible.

## B) Scheduler por micro-hitos (no esperar heartbeat)
- Después de cada tarea cerrada, programar inmediatamente la siguiente localmente (cola interna de tareas en memoria de sesión).
- Heartbeat se usa como “watchdog”, no como motor principal.

## C) Métrica de “vida percibida” (Liveness Index)
Nuevo KPI para validar avance real:
- Nº pensamientos internos / hora
- Nº pensamientos vocalizados / hora
- Ratio de novedad semántica
- Varianza neuroquímica

Si sube este índice, Franqui “vive más”.

## D) Presupuesto cognitivo nocturno
No dejarlo “hablando toda la noche” sin control:
- límite de vocalizaciones por hora
- más pensamiento interno que hablado durante sueño
- priorizar consolidación sobre salida sonora

## E) Memoria autobiográfica mínima
Cada cierto número de pensamientos, guardar una frase “hoy me di cuenta de X”
para construir continuidad de identidad (no solo logs técnicos).

---

## Riesgos y mitigación
- Riesgo: fatiga sonora → **mitigar con policy por hora y prioridad**
- Riesgo: loops triviales → **surprise threshold + novelty filter**
- Riesgo: deriva incoherente → **homeostasis + replay guiado por episodios reales**

---

## Criterio de éxito (definición de DONE)
- Franqui responde con voz SIEMPRE en interacción reactiva
- En idle genera pensamiento interno continuo
- Una parte de ese pensamiento se oye según reglas neuroquímicas
- `/brain` + `/chem` + (nuevo) `/inner` muestran trazabilidad de vida interna
- Tests en verde + smoke test nocturno controlado
