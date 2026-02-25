# Plan de mejoras post-brainstorm (Dr. OpenClaw)
**Fecha:** 2026-02-25 18:32
**Fuente revisada:** `docs/brainstorm_equipo_supervision.md`

## Decisiones: qué adopto ya, qué adapto, qué descarto (de momento)

## 1) Adopción inmediata (prioridad alta)

### A. Hardening SQLite en `MemorySystem`
- Añadir/confirmar pragmas al iniciar conexión:
  - `journal_mode=WAL` (ya está)
  - `synchronous=NORMAL`
  - `busy_timeout=5000`
  - `cache_size=-8000`
- **Motivo:** reducir riesgo de lock/corrupción en escrituras concurrentes.

### B. Aislamiento de tests (fixture único)
- Crear helper/fixture reutilizable `isolated_being()` para que TODOS los tests que usan `Being` vayan siempre contra DB efímera.
- **Motivo:** evitar contaminación producción/tests y falsos positivos.

### C. Backup automático pre-training
- Implementar utilidad `auto_backup(db_path)` + retención (últimos 5).
- Ejecutar antes de cualquier bloque masivo de training o migración.
- **Motivo:** disciplina operativa y rollback rápido.

### D. Prompt LLM con feedback histórico
- Ya iniciado en bloque anterior: mantener y afinar top ejemplos bien puntuados.
- **Motivo:** few-shot real del usuario mejora alineación de estilo.

## 2) Adopción en siguiente iteración (prioridad media)

### E. Curiosidad v2 con scoring de valor
- No solo menor confianza; usar score mixto:
  - baja confianza
  - nº asociaciones
  - recencia de refuerzo
- **Motivo:** curiosidad más útil, menos ruido.

### F. Métricas de curiosidad
- Exponer:
  - `runs_total`
  - `runs_last_hour`
  - `topics_explored_today`
  - `avg_answer_length`
- **Motivo:** observabilidad objetiva del motor autónomo.

### G. Ciclo de sueño ligero
- Consolidación + maintenance + reflect + 1-3 pasos curiosidad con límites.
- Activar sólo en ventanas de inactividad.
- **Motivo:** aprendizaje de fondo sin saturación.

## 3) Diseño preparado (aún no activar)

### H. Campo `source` en episodios
- Propuesta:
  - `user | training | curiosity | test`
- Requiere migración y compatibilidad.
- **Motivo:** trazabilidad de calidad de memoria.

### I. Voz KittenTTS Hugo por eventos
- Activar sólo en eventos de alto impacto:
  - level up
  - descubrimiento curioso
  - insight de reflexión
- **Motivo:** evitar fatiga sonora y mantener valor.

## 4) Mis mejoras adicionales (no estaban explícitas)

### J. Health-check automático de DB al arranque
- `PRAGMA integrity_check` al boot.
- Si falla:
  1) poner modo read-safe
  2) backup inmediato
  3) iniciar rutina de reparación guiada
- **Motivo:** detección temprana y reducción de daño.

### K. Modo “safe training”
- Bloquear entrenamiento masivo si no existe backup reciente (ej: <30 min).
- **Motivo:** forzar higiene operativa.

### L. Reporting anti-gaps
- Si un bloque supera X interacciones sin reporte, generar mini-reporte automático.
- **Motivo:** no volver a tener saltos grandes no documentados.

## 5) Roadmap operativo (orden de ejecución)
1. Hardening SQLite + fixture aislamiento + auto-backup.
2. Curiosidad v2 (scoring) + métricas.
3. Sleep cycle ligero con guardrails.
4. Preparar migración `source` episodios.
5. Integración de voz Hugo por eventos (cuando estabilidad esté validada).

## 6) Criterios de “done”
- Tests verdes + test nuevo por cada módulo añadido.
- Report completo por bloque (sin gaps).
- DB integrity check en `ok` antes y después de sesiones de entrenamiento.
- Backups automáticos verificables en disco.
