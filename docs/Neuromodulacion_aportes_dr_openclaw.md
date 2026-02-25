# Neuromodulación — aportes propios de Dr. OpenClaw
**Fecha:** 2026-02-25

## Lo que añado al diseño (más allá del documento base)

## 1) Gating adaptativo por confianza (no solo por química)
Además del estado neuroquímico, el grafo debería considerar la **confianza cognitiva local**:
- Si el pico de activación < umbral de confianza, usar respuesta corta + pedir clarificación.
- Si el pico > umbral alto, permitir respuestas más elaboradas.

Esto evita que dopamina alta genere “overconfidence” con base débil.

## 2) Reconciliación química↔feedback en doble tiempo
Propongo dos ventanas:
- **Fast loop (segundos):** modulación por evento (feedback, curiosidad, error).
- **Slow loop (minutos):** homeostasis ponderada por tendencia de sesión.

Si la sesión lleva feedback positivo sostenido, la línea base de dopamina/oxitocina sube ligeramente; si hay fricción prolongada, sube baseline de norepinefrina y baja amplitud exploratoria.

## 3) Memoria sesgada por estado (retrieval state-dependent)
No basta con cambiar activación del grafo: también debe cambiar qué recuerdos se consultan.
- Cortisol alto: priorizar episodios recientes y concretos (seguridad/acción).
- Serotonina alta: abrir búsqueda semántica más amplia (asociaciones lejanas).
- Oxitocina alta: priorizar episodios del usuario actual (vínculo personalizado).

## 4) Curiosidad condicionada por “ventana metabólica”
Curiosity engine debería disparar solo si:
- dopamine > 0.45
- cortisol < 0.55
- norepinephrine en rango medio (ni apatía ni saturación)

Así evitamos curiosidad en modo “estrés” o “ruido”.

## 5) Índice de salud neurocognitiva (NHI)
Nuevo KPI para `/chem` y reportes:

`NHI = (dopamine*0.25 + serotonin*0.25 + oxytocin*0.2 + (1-cortisol)*0.2 + stability*0.1)`

Donde `stability` depende de varianza reciente de moduladores. Sirve para detectar estados inestables antes de degradación conductual.

## 6) Antifragilidad: detección de anomalías internas
Si hay errores recurrentes (DB, fallback, timeouts), aumentar norepinefrina/cortisol y activar modo "safe cognition":
- respuestas más breves
- menor profundidad de propagación
- priorizar exactitud sobre creatividad

## 7) Voice policy neuromodulada (Hugo)
La voz no debería ser solo por evento, también por química:
- Oxitocina + dopamina altas → mensajes cálidos/celebración
- Cortisol alto → evitar voz para no amplificar fricción
- Norepinefrina alta → voz solo en alertas críticas

## 8) Experimentos controlados A/B
Antes de consolidar parámetros, correr A/B en 3 perfiles:
- explorador (dopamina alta)
- reflexivo (serotonina alta)
- foco defensivo (norepinefrina/cortisol altas)

Métricas: coherencia, utilidad percibida, tasa de clarificación, longitud de respuesta.

## 9) Riesgos principales y mitigación
- **Oscilación química extrema:** aplicar smoothing exponencial + clamps.
- **Sobresesgo afectivo:** cap a la influencia de moduladores sobre umbral.
- **Narrativa incoherente entre turnos:** persistir estado + decaimiento gradual, nunca saltos bruscos.

## 10) Orden recomendado de evolución
1. Estabilizar modulación actual + observabilidad `/chem`.
2. Añadir retrieval state-dependent.
3. Activar gating de curiosidad por ventana metabólica.
4. Introducir NHI y alertas.
5. Integrar voz neuromodulada.
