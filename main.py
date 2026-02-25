"""Franquenstein — A self-learning digital being.

Main entry point. Run this to bring Franquenstein to life.

Usage:
    python main.py
"""

from franquenstein.being import Being
from franquenstein.interface.console import ConsoleInterface
from franquenstein.perception import read_document, fetch_web_text
from franquenstein.memory.backup import auto_backup
from franquenstein.config import (
    VOICE_ENABLED,
    VOICE_COOLDOWN_SECONDS,
    VOICE_TRIGGER_CURIOSITY,
    VOICE_TRIGGER_LEVELUP,
)

import subprocess
import time
from pathlib import Path


def _learn_from_external_text(being: Being, text: str, chunk_size: int = 300) -> int:
    """Feed external text into the normal interaction-learning pipeline.

    Returns number of chunks successfully processed.
    """
    clean = " ".join(text.split())
    if not clean:
        return 0

    chunks = [clean[i:i + chunk_size] for i in range(0, len(clean), chunk_size)]
    learned = 0
    for chunk in chunks:
        if len(chunk.strip()) < 20:
            continue
        result = being.interact(chunk)
        score = 0.7 if result.get("response") else 0.4
        being.give_feedback(score)
        learned += 1
    return learned


_last_voice_ts = 0.0


def _try_voice_event(text: str) -> None:
    """Speak short high-value events with KittenTTS Hugo (best-effort)."""
    global _last_voice_ts
    if not VOICE_ENABLED:
        return
    now = time.time()
    if now - _last_voice_ts < VOICE_COOLDOWN_SECONDS:
        return

    script = Path("/home/dfara/.openclaw/workspace/scripts/kitten_speak.py")
    if not script.exists():
        return

    try:
        subprocess.Popen(["python3", str(script), text])
        _last_voice_ts = now
    except Exception:
        pass


def main() -> None:
    """Start Franquenstein and run the interaction loop."""

    # Initialize systems
    being = Being()
    ui = ConsoleInterface()

    # Show startup
    ui.show_startup(
        level=being.level,
        level_name=being.level_name,
        mood=being.mood,
    )

    # Run maintenance on startup (consolidate, decay)
    maintenance = being.memory.maintenance()
    neural_maintenance = being.neural.decay()
    if neural_maintenance.get("synapses_pruned", 0) > 0:
        ui.show_system_message(
            f"Neural pruning: {neural_maintenance['synapses_pruned']} weak synapses removed."
        )

    if maintenance["concepts_consolidated"] > 0:
        ui.show_system_message(
            f"Consolidated {maintenance['concepts_consolidated']} concepts while sleeping."
        )
    if maintenance["memories_decayed"] > 0:
        ui.show_system_message(
            f"Faded {maintenance['memories_decayed']} old memories."
        )

    # ─── Main interaction loop ───────────────────────────────
    try:
        while True:
            # Get user input
            user_input = ui.show_user_prompt()

            if not user_input:
                continue

            # ── Handle special commands ──
            if user_input.startswith("/"):
                command = user_input.lower().strip()

                if command == "/quit" or command == "/exit":
                    break

                elif command == "/help":
                    ui.show_help()

                elif command == "/stats":
                    ui.show_stats(
                        memory_stats=being.memory.get_stats(),
                        learning_stats=being.learner.get_stats(),
                        growth_status=being.growth.get_status_display(),
                    )

                elif command == "/memory":
                    recent = being.memory.episodic.recall_recent(5)
                    concepts = being.memory.semantic.get_confident(
                        min_confidence=0.2, limit=15
                    )
                    ui.show_memory(recent, concepts)

                elif command == "/brain":
                    stats = being.neural.get_stats()
                    ui.show_system_message(
                        f"🧠 Neural Graph: {stats['total_nodes']} nodes, {stats['total_synapses']} synapses | "
                        f"avg_w={stats['avg_synapse_weight']} | top='{stats['most_fired_node']}' ({stats['most_fired_count']})"
                    )

                elif command == "/chem":
                    c = being.chemistry_state
                    ui.show_system_message(
                        "🧪 Neurochemistry | "
                        f"D={c['dopamine']:.2f} S={c['serotonin']:.2f} N={c['norepinephrine']:.2f} "
                        f"C={c['cortisol']:.2f} O={c['oxytocin']:.2f}"
                    )

                elif command == "/level":
                    ui.show_progress(being.growth.get_progress())

                elif command == "/reflect":
                    reflections = being.learner.metacognition.reflect()
                    ui.show_reflection(reflections)

                elif command == "/curious":
                    result = being.curiosity_step()
                    if result.get("status") == "ok":
                        ui.show_system_message(
                            f"Curiosity explored '{result.get('concept')}'."
                        )
                        ui.show_response(result.get("answer", ""), emotion="curiosidad")
                        if VOICE_TRIGGER_CURIOSITY:
                            _try_voice_event(
                                f"Descubrí algo nuevo sobre {result.get('concept')}"
                            )
                    elif result.get("status") == "locked":
                        ui.show_error("Curiosity is unlocked at Level 2.")
                    else:
                        ui.show_system_message("No suitable curiosity target found yet.")

                elif command.startswith("/feedback "):
                    # /feedback 0.5 → positive, /feedback -0.5 → negative
                    try:
                        score = float(command.split()[1])
                        result = being.give_feedback(score)
                        if result.get("reflection"):
                            ui.show_system_message(f"Reflection: {result['reflection']}")
                        else:
                            ui.show_system_message("Feedback received. Thank you!")
                    except (ValueError, IndexError):
                        ui.show_error("Usage: /feedback <score> (e.g., /feedback 0.5)")

                elif user_input.strip().lower().startswith("/learn "):
                    target = user_input.strip()[7:].strip()
                    if not target:
                        ui.show_error("Usage: /learn <path_or_url>")
                        continue

                    try:
                        if target.startswith(("http://", "https://")):
                            content = fetch_web_text(target)
                            source = "web"
                        else:
                            content = read_document(target)
                            source = "file"

                        # Safety gate: backup memory DB before external mass-learning.
                        backup_path = auto_backup(being.memory._db_path)
                        ui.show_system_message(f"Backup created: {backup_path.name}")

                        learned_chunks = _learn_from_external_text(being, content)
                        if learned_chunks == 0:
                            ui.show_error("No useful content found to learn from.")
                        else:
                            ui.show_system_message(
                                f"Learned from {source}: {learned_chunks} chunks processed."
                            )
                    except Exception as exc:
                        ui.show_error(f"/learn failed: {exc}")

                else:
                    ui.show_error(f"Unknown command: {command}. Type /help for options.")

                continue

            # ── Normal interaction ──
            result = being.interact(user_input)

            # Show response with emotion
            ui.show_response(
                text=result["response"],
                emotion=result["emotion"],
            )

            # Show learning indicators (subtle)
            ui.show_learning(result["learning"])

            # Show level-up if it happened!
            if result["growth"]:
                ui.show_level_up(
                    old_level=result["growth"]["old_level"],
                    new_level=result["growth"]["new_level"],
                    old_name=result["growth"]["old_name"],
                    new_name=result["growth"]["new_name"],
                )
                if VOICE_TRIGGER_LEVELUP:
                    _try_voice_event(
                        f"Subí de nivel. Ahora soy {result['growth']['new_name']}"
                    )

    except KeyboardInterrupt:
        pass  # Graceful exit on Ctrl+C

    # ─── Shutdown ────────────────────────────────────────────
    ui.show_goodbye(being.interaction_count)
    being.shutdown()


if __name__ == "__main__":
    main()
