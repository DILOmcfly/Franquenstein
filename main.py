"""Franquenstein — main runtime."""

from __future__ import annotations

import json
import queue
import random
import sqlite3
import subprocess
import threading
import time
from pathlib import Path

from franquenstein.being import Being
from franquenstein.interface.console import ConsoleInterface
from franquenstein.memory.backup import auto_backup
from franquenstein.neural import NeuralGraph, ResponseWeaver
from franquenstein.perception import fetch_web_text, read_document
from franquenstein.config import (
    VOICE_COOLDOWN_SECONDS,
    VOICE_ENABLED,
    VOICE_SCRIPT,
    VOICE_TRIGGER_CURIOSITY,
    VOICE_TRIGGER_LEVELUP,
    VOICE_TRIGGER_NORMAL_RESPONSE,
)

VOICE_PRIORITY_LEVELUP = 1
VOICE_PRIORITY_EMOTION = 2
VOICE_PRIORITY_REACTIVE = 3
VOICE_PRIORITY_INNER = 4


def _learn_from_external_text(being: Being, text: str, chunk_size: int = 300) -> int:
    clean = " ".join(text.split())
    if not clean:
        return 0
    chunks = [clean[i : i + chunk_size] for i in range(0, len(clean), chunk_size)]
    learned = 0
    for chunk in chunks:
        if len(chunk.strip()) < 20:
            continue
        result = being.interact(chunk)
        being.give_feedback(0.7 if result.get("response") else 0.4)
        learned += 1
    return learned


class VoiceEngine:
    def __init__(self):
        self.enabled = VOICE_ENABLED
        self.cooldown = float(VOICE_COOLDOWN_SECONDS)
        self._last_spoke = 0.0
        self._q: queue.PriorityQueue[tuple[int, float, str]] = queue.PriorityQueue()
        self._stop = threading.Event()
        self._worker = threading.Thread(target=self._loop, daemon=True)
        self._script = Path(VOICE_SCRIPT)
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self._started = True
        self._worker.start()

    def stop(self) -> None:
        self._stop.set()

    def speak(self, text: str, priority: int = 1) -> None:
        if not self.enabled or not text.strip():
            return
        self._q.put((max(1, min(5, priority)), time.time(), text.strip()))

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                prio, ts, text = self._q.get(timeout=0.5)
            except queue.Empty:
                continue
            now = time.time()
            if now - self._last_spoke < self.cooldown and prio > 1:
                self._q.put((prio, ts, text))
                time.sleep(0.2)
                continue
            if not self._script.exists():
                continue
            try:
                subprocess.Popen(["python3", str(self._script), text])
                self._last_spoke = time.time()
            except Exception:
                pass


class InnerWorld:
    def __init__(self, being: Being, voice: VoiceEngine, last_interaction_ref: list[float]):
        self.being = being
        self.voice = voice
        self.last_interaction_ref = last_interaction_ref
        self.db_path = being.memory._db_path
        self.running = False
        self._thread: threading.Thread | None = None
        self.inner_log: list[dict] = []

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self.running = False

    def snapshot(self, limit: int = 5) -> list[dict]:
        return self.inner_log[-limit:]

    def _loop(self) -> None:
        own_conn = sqlite3.connect(str(self.db_path))
        own_conn.execute("PRAGMA journal_mode=WAL")
        own_neural = NeuralGraph(own_conn)
        own_weaver = ResponseWeaver(own_neural)
        try:
            while self.running:
                idle = time.time() - self.last_interaction_ref[0]
                if idle < 25:
                    time.sleep(5)
                    continue
                thought = self.inner_thought_step(idle, own_neural, own_weaver)
                if thought:
                    self.inner_log.append(thought)
                    if len(self.inner_log) > 200:
                        self.inner_log = self.inner_log[-120:]
                    try:
                        now = time.time()
                        hk = time.strftime("inner_thoughts_hour_%Y%m%d_%H", time.localtime(now))
                        tk = "inner_thoughts_total"
                        payload = json.dumps(self.inner_log[-20:], ensure_ascii=False)

                        def _inc(key: str):
                            row = own_conn.execute("SELECT value FROM being_state WHERE key=?", (key,)).fetchone()
                            cur = int(row[0]) if row else 0
                            val = str(cur + 1)
                            own_conn.execute(
                                "INSERT INTO being_state (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
                                (key, val),
                            )

                        _inc(hk)
                        _inc(tk)
                        own_conn.execute(
                            "INSERT INTO being_state (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
                            ("inner_log_recent", payload),
                        )
                        own_conn.commit()
                    except Exception:
                        pass

                    can_speak = self.being.chemistry.serotonin > 0.45 and self.being.chemistry.cortisol < 0.6
                    if can_speak and (thought["energy"] > 0.55 or thought["surprise"] > 0.6):
                        self.voice.speak(f"Hmm... {thought['verbalized']}", priority=VOICE_PRIORITY_INNER)
                        try:
                            vk = time.strftime("inner_voiced_hour_%Y%m%d_%H", time.localtime())
                            row = own_conn.execute("SELECT value FROM being_state WHERE key=?", (vk,)).fetchone()
                            cur = int(row[0]) if row else 0
                            own_conn.execute(
                                "INSERT INTO being_state (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
                                (vk, str(cur + 1)),
                            )
                            own_conn.commit()
                        except Exception:
                            pass

                time.sleep(15 if idle > 300 else 30)
        finally:
            own_conn.close()

    def inner_thought_step(self, idle_seconds: float, neural: NeuralGraph, weaver: ResponseWeaver) -> dict | None:
        cur = neural._conn.cursor()
        seed = None
        if random.random() < 0.6:
            r = cur.execute("SELECT label FROM neural_nodes WHERE node_type='concept' ORDER BY fire_count ASC LIMIT 1").fetchone()
            if r:
                seed = r[0]
        if not seed:
            rows = cur.execute("SELECT label FROM neural_nodes WHERE node_type='concept' ORDER BY fire_count DESC LIMIT 10").fetchall()
            if rows:
                seed = random.choice([x[0] for x in rows])
        if not seed:
            return None

        params = self.being.chemistry.get_graph_params()
        activation = neural.activate([seed], params=params)
        verbalized = weaver.weave(activation=activation, input_text=seed, graph_stats=neural.get_stats(), tone=self.being.chemistry.get_tone())
        if not verbalized:
            verbalized = f"{seed}... sigo intentando conectar mejor esta idea."
        conns = neural.get_strongest_connections(seed, limit=3)
        surprise = 0.8 if len(conns) == 0 else max(0.1, 0.5 - (conns[0][1] * 0.4))
        return {
            "timestamp": time.time(),
            "seed": seed,
            "energy": float(activation.peak_energy or 0.0),
            "surprise": float(surprise),
            "verbalized": verbalized,
            "idle_seconds": round(idle_seconds, 1),
        }


def main() -> None:
    being = Being()
    ui = ConsoleInterface()
    last_interaction = [time.time()]
    voice = VoiceEngine(); voice.start()
    inner = InnerWorld(being, voice, last_interaction); inner.start()

    ui.show_startup(level=being.level, level_name=being.level_name, mood=being.mood)

    maintenance = being.memory.maintenance()
    neural_maintenance = being.neural.decay()
    if neural_maintenance.get("synapses_pruned", 0) > 0:
        ui.show_system_message(f"Neural pruning: {neural_maintenance['synapses_pruned']} weak synapses removed.")
    if maintenance["concepts_consolidated"] > 0:
        ui.show_system_message(f"Consolidated {maintenance['concepts_consolidated']} concepts while sleeping.")
    if maintenance["memories_decayed"] > 0:
        ui.show_system_message(f"Faded {maintenance['memories_decayed']} old memories.")

    try:
        while True:
            user_input = ui.show_user_prompt()
            if not user_input:
                continue
            last_interaction[0] = time.time()

            if user_input.startswith("/"):
                command = user_input.lower().strip()
                if command in {"/quit", "/exit"}:
                    break
                elif command == "/help":
                    ui.show_help()
                elif command == "/stats":
                    ui.show_stats(memory_stats=being.memory.get_stats(), learning_stats=being.learner.get_stats(), growth_status=being.growth.get_status_display())
                elif command == "/memory":
                    ui.show_memory(being.memory.episodic.recall_recent(5), being.memory.semantic.get_confident(min_confidence=0.2, limit=15))
                elif command == "/brain":
                    stats = being.neural.get_stats(); top = stats.get("most_fired_node")
                    msg = f"🧠 Neural Graph: {stats['total_nodes']} nodes, {stats['total_synapses']} synapses | avg_w={stats['avg_synapse_weight']} | top='{top}' ({stats['most_fired_count']})"
                    if top:
                        conns = being.neural.get_strongest_connections(top, limit=3)
                        if conns:
                            msg += " | links[" + ", ".join([f"{l}:{w:.2f}" for l, w in conns]) + "]"
                    ui.show_system_message(msg)
                elif command == "/chem":
                    c = being.chemistry_state
                    ui.show_system_message(f"🧪 Neurochemistry | D={c['dopamine']:.2f} S={c['serotonin']:.2f} N={c['norepinephrine']:.2f} C={c['cortisol']:.2f} O={c['oxytocin']:.2f}")
                elif command == "/inner":
                    thoughts = inner.snapshot(limit=3)
                    if not thoughts:
                        ui.show_system_message("No inner thoughts yet.")
                    else:
                        for t in thoughts:
                            ui.show_system_message(f"🫧 [{int(t['idle_seconds'])}s idle] {t['verbalized']}")
                elif command == "/innerstats":
                    hk = time.strftime("inner_thoughts_hour_%Y%m%d_%H", time.localtime())
                    vk = time.strftime("inner_voiced_hour_%Y%m%d_%H", time.localtime())
                    ui.show_system_message(f"🫧 InnerStats | thoughts/h={int(being.memory.load_state(hk,'0'))} voiced/h={int(being.memory.load_state(vk,'0'))} total={int(being.memory.load_state('inner_thoughts_total','0'))}")
                elif command == "/level":
                    ui.show_progress(being.growth.get_progress())
                elif command == "/reflect":
                    ui.show_reflection(being.learner.metacognition.reflect())
                elif command == "/curious":
                    result = being.curiosity_step()
                    if result.get("status") == "ok":
                        ui.show_system_message(f"Curiosity explored '{result.get('concept')}'.")
                        ui.show_response(result.get("answer", ""), emotion="curiosidad")
                        if VOICE_TRIGGER_CURIOSITY:
                            voice.speak(f"Descubrí algo nuevo sobre {result.get('concept')}", priority=VOICE_PRIORITY_EMOTION)
                    elif result.get("status") == "locked":
                        ui.show_error("Curiosity is unlocked at Level 2.")
                    else:
                        ui.show_system_message("No suitable curiosity target found yet.")
                elif command.startswith('/feedback '):
                    try:
                        score = float(command.split()[1])
                        res = being.give_feedback(score)
                        ui.show_system_message(f"Reflection: {res['reflection']}") if res.get('reflection') else ui.show_system_message('Feedback received. Thank you!')
                    except (ValueError, IndexError):
                        ui.show_error('Usage: /feedback <score> (e.g., /feedback 0.5)')
                elif user_input.strip().lower().startswith('/learn '):
                    target = user_input.strip()[7:].strip()
                    if not target:
                        ui.show_error('Usage: /learn <path_or_url>'); continue
                    try:
                        content = fetch_web_text(target) if target.startswith(('http://','https://')) else read_document(target)
                        source = 'web' if target.startswith(('http://','https://')) else 'file'
                        backup = auto_backup(being.memory._db_path)
                        ui.show_system_message(f"Backup created: {backup.name}")
                        n = _learn_from_external_text(being, content)
                        ui.show_error('No useful content found to learn from.') if n == 0 else ui.show_system_message(f"Learned from {source}: {n} chunks processed.")
                    except Exception as exc:
                        ui.show_error(f"/learn failed: {exc}")
                else:
                    ui.show_error(f"Unknown command: {command}. Type /help for options.")
                continue

            result = being.interact(user_input)
            ui.show_response(text=result['response'], emotion=result['emotion'])
            if VOICE_TRIGGER_NORMAL_RESPONSE:
                voice.speak(result['response'], priority=VOICE_PRIORITY_REACTIVE)
            ui.show_learning(result['learning'])
            if result['growth']:
                ui.show_level_up(old_level=result['growth']['old_level'], new_level=result['growth']['new_level'], old_name=result['growth']['old_name'], new_name=result['growth']['new_name'])
                if VOICE_TRIGGER_LEVELUP:
                    voice.speak(f"Subí de nivel. Ahora soy {result['growth']['new_name']}", priority=VOICE_PRIORITY_LEVELUP)
    except KeyboardInterrupt:
        pass
    finally:
        inner.stop(); voice.stop(); being.shutdown()
        ui.show_goodbye(being.interaction_count)


if __name__ == '__main__':
    main()
