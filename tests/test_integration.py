"""Integration test for Franquenstein — tests the full cognitive cycle."""

import os
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from franquenstein.being import Being
from franquenstein.memory.memory import MemorySystem
from franquenstein.memory.working import WorkingMemory, WorkingMemoryItem
from franquenstein.memory.episodic import EpisodicMemory
from franquenstein.memory.semantic import SemanticMemory
from franquenstein.memory.emotional import EmotionalMemory
from franquenstein.learning.patterns import PatternDetector
from franquenstein.growth.growth import GrowthSystem
from franquenstein.perception.reader import read_document
from franquenstein.perception.web import fetch_web_text
from main import _learn_from_external_text
from franquenstein.memory.backup import auto_backup


@contextmanager
def isolated_being():
    """Being with isolated temporary DB (never touches production)."""
    import franquenstein.config as cfg

    original = cfg.DB_PATH
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg.DB_PATH = Path(tmpdir) / "isolated_test.db"
        being = Being()
        try:
            yield being
        finally:
            being.shutdown()
            cfg.DB_PATH = original



def test_working_memory():
    """Test working memory buffer."""
    print("Testing Working Memory...", end=" ")
    wm = WorkingMemory(capacity=3)

    assert wm.is_empty
    assert wm.size == 0

    wm.push(WorkingMemoryItem(input_text="hello", output_text="hi"))
    wm.push(WorkingMemoryItem(input_text="how are you", output_text="good"))
    wm.push(WorkingMemoryItem(input_text="what's up", output_text="sky"))

    assert wm.size == 3

    # Test overflow
    wm.push(WorkingMemoryItem(input_text="new item", output_text="newest"))
    assert wm.size == 3  # Should still be 3 (oldest dropped)

    # Test search
    results = wm.search("new")
    assert len(results) >= 1

    # Test context string
    context = wm.get_context_string()
    assert "new item" in context

    print("✅ PASSED")


def test_memory_system():
    """Test the full memory system with a temp database."""
    print("Testing Memory System...", end=" ")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_memory.db"
        memory = MemorySystem(db_path=db_path)

        # Test remember
        ep_id = memory.remember(
            input_text="Hello world",
            output_text="Hi there!",
            emotion="curiosidad",
            emotion_intensity=0.7,
        )
        assert ep_id > 0

        # Test recall
        results = memory.recall("hello")
        assert len(results["episodic"]) > 0

        # Test semantic learning
        memory.semantic.learn_concept("python", definition="A programming language")
        concept = memory.semantic.get_concept("python")
        assert concept is not None
        assert concept.concept == "python"

        # Test emotional memory
        memory.emotional.feel("python", "curiosidad", 0.8)
        feelings = memory.emotional.get_feelings_about("python")
        assert len(feelings) > 0

        # Test stats
        stats = memory.get_stats()
        assert stats["episodic_memories"] >= 1
        assert stats["semantic_concepts"] >= 1

        # Test state persistence
        memory.save_state("test_key", "test_value")
        assert memory.load_state("test_key") == "test_value"

        memory.close()

    print("✅ PASSED")


def test_pattern_detection():
    """Test pattern detection."""
    print("Testing Pattern Detection...", end=" ")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_patterns.db"
        memory = MemorySystem(db_path=db_path)
        detector = PatternDetector(memory._conn)

        # Observe text multiple times
        detector.observe("hello world")
        detector.observe("hello world")
        new_patterns = detector.observe("hello world")

        # After 3 observations, patterns should become "known"
        assert len(new_patterns) > 0

        # Check known words
        known = detector.get_known_words(min_frequency=3)
        word_names = [w[0] for w in known]
        assert "hello" in word_names or "world" in word_names

        # Test response patterns
        detector.observe_response("hello", "hi there!", feedback_score=0.8)
        detector.observe_response("hello", "hi there!", feedback_score=0.9)
        best = detector.get_best_response("hello")
        assert best == "hi there!"

        memory.close()

    print("✅ PASSED")


def test_being_interaction():
    """Test the full being interaction cycle."""
    print("Testing Being Interaction...", end=" ")

    with isolated_being() as being:
        # Test basic interaction
        result = being.interact("Hello!")
        assert "response" in result
        assert "emotion" in result
        assert "learning" in result

        # Test name detection
        result2 = being.interact("My name is David")
        assert "David" in result2["response"] or being._user_name == "David"

        # Test multiple interactions
        for i in range(5):
            r = being.interact(f"Tell me about topic {i}")
            assert r["response"] != ""

        # Verify memories were stored
        assert being.memory.episodic.count() >= 7  # At least our interactions
        assert being.interaction_count >= 7

    print("✅ PASSED")


def test_growth_system():
    """Test the growth/leveling system."""
    print("Testing Growth System...", end=" ")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_growth.db"
        memory = MemorySystem(db_path=db_path)
        growth = GrowthSystem(memory)

        # Initially level 0
        assert growth.level == 0
        assert growth.level_name == "Bebé"
        assert growth.can("echo")
        assert growth.can("basic_response")
        assert not growth.can("ask_questions")

        # Test progress display
        progress = growth.get_progress()
        assert progress["current_level"] == 0

        # Simulate enough experiences for level 1
        for i in range(25):
            memory.remember(
                input_text=f"test input {i}",
                output_text=f"test output {i}",
            )

        # Add enough vocabulary
        for word in ["alpha", "beta", "gamma", "delta", "epsilon",
                      "zeta", "eta", "theta", "iota", "kappa", "lambda"]:
            memory.semantic.learn_concept(word)

        # Check growth
        result = growth.check_growth()
        assert result is not None
        assert result["new_level"] >= 1
        assert growth.can("remember_name")

        memory.close()

    print("✅ PASSED")


def test_llm_fallback_stability():
    """Ensure Being falls back safely when LLM path errors at Level 2+."""
    print("Testing LLM Fallback Stability...", end=" ")

    with isolated_being() as being:
        # Prepare enough growth to reach level 2
        for i in range(120):
            being.interact(f"learning sample interaction {i}")
        for i in range(80):
            being.memory.semantic.learn_concept(f"concept_l2_{i}")
        being.growth.check_growth()

        assert being.level >= 2

        # Force LLM availability true, but generation failure
        class _BrokenLLM:
            def is_available(self):
                return True

            def generate(self, **kwargs):
                raise RuntimeError("simulated llm failure")

        being._llm_reasoner = _BrokenLLM()
        result = being.interact("Explain what memory means")

        # Should still provide a response via fallback path
        assert isinstance(result["response"], str)
        assert len(result["response"].strip()) > 0

    print("✅ PASSED")


def test_document_reader_txt_md():
    """Test external file reading for .txt and .md."""
    print("Testing Document Reader (.txt/.md)...", end=" ")

    with tempfile.TemporaryDirectory() as tmpdir:
        txt = Path(tmpdir) / "sample.txt"
        md = Path(tmpdir) / "sample.md"
        txt.write_text("hello from txt", encoding="utf-8")
        md.write_text("# title\nhello from md", encoding="utf-8")

        t = read_document(str(txt))
        m = read_document(str(md))

        assert "hello from txt" in t
        assert "hello from md" in m

    print("✅ PASSED")


def test_fetch_web_text_local_file_url():
    """Test web fetcher with a local file:// URL as lightweight mock."""
    print("Testing Web Fetch (file:// mock)...", end=" ")

    with tempfile.TemporaryDirectory() as tmpdir:
        html = Path(tmpdir) / "sample.html"
        html.write_text(
            "<html><body><h1>Title</h1><p>Hello Franquenstein web learning</p></body></html>",
            encoding="utf-8",
        )
        text = fetch_web_text(html.resolve().as_uri())
        assert "Title" in text
        assert "Hello Franquenstein web learning" in text

    print("✅ PASSED")


def test_learn_command_pipeline_local_text():
    """E2E-ish test for /learn pipeline helper using local text content."""
    print("Testing /learn Pipeline Helper...", end=" ")

    with isolated_being() as being:
        before = being.memory.episodic.count()

        content = (
            "Learning from external sources improves adaptability. "
            "Franquenstein can ingest structured text and retain concepts over time."
        )
        processed = _learn_from_external_text(being, content, chunk_size=80)

        after = being.memory.episodic.count()
        assert processed > 0
        assert after > before

    print("✅ PASSED")


def test_curiosity_step_generates_episode():
    """Curiosity step should create a proactive learning episode at Level 2+."""
    print("Testing Curiosity Step...", end=" ")

    with isolated_being() as being:
        # Reach level 2 quickly
        for i in range(120):
            being.interact(f"curiosity training sample {i}")
        for i in range(80):
            being.memory.semantic.learn_concept(f"concept_cur_{i}")
        being.growth.check_growth()
        assert being.level >= 2

        being._last_curiosity_ts = 0
        being._curiosity_timestamps = []

        before = being.memory.episodic.count()
        result = being.curiosity_step()
        after = being.memory.episodic.count()

        assert result.get("status") in {"ok", "no_candidates", "throttled"}
        if result.get("status") == "ok":
            assert after > before
            assert result.get("answer")

    print("✅ PASSED")


def test_curiosity_throttling_guardrails():
    """Curiosity should be throttled on immediate consecutive calls."""
    print("Testing Curiosity Throttling...", end=" ")

    with isolated_being() as being:
        for i in range(120):
            being.interact(f"throttle training sample {i}")
        for i in range(80):
            being.memory.semantic.learn_concept(f"concept_thr_{i}")
        being.growth.check_growth()
        assert being.level >= 2

        being._last_curiosity_ts = 0
        being._curiosity_timestamps = []

        first = being.curiosity_step()
        second = being.curiosity_step()

        assert first.get("status") in {"ok", "no_candidates", "throttled"}
        # If first succeeded, second should usually throttle due to cooldown.
        if first.get("status") == "ok":
            assert second.get("status") == "throttled"

    print("✅ PASSED")




def test_auto_backup_utility():
    """Backup utility should create timestamped copy and keep retention."""
    print("Testing Auto Backup Utility...", end=" ")

    with tempfile.TemporaryDirectory() as tmpdir:
        db = Path(tmpdir) / "memory.db"
        db.write_bytes(b"sqlite-mock")

        b1 = auto_backup(db, keep_last=2)
        assert b1.exists()
        b2 = auto_backup(db, keep_last=2)
        assert b2.exists()
        b3 = auto_backup(db, keep_last=2)
        assert b3.exists()

        backups = sorted(db.parent.glob("memory_backup_*.db"))
        assert len(backups) <= 2

    print("✅ PASSED")


def test_offline_response_patterns():
    """With LLM unavailable, known taught questions should be answered from patterns."""
    print("Testing Offline Response Patterns...", end=" ")

    with isolated_being() as being:
        lessons = [
            ("¿Qué es Python?", "Python es un lenguaje de programación muy popular."),
            ("¿Qué es la memoria?", "La memoria es la capacidad de recordar información."),
        ]

        # Teach explicitly with repeated positive feedback + supervised response-pattern seed
        for q, ideal in lessons:
            for _ in range(2):
                being.interact(q)
                being.give_feedback(0.8)
                being.learner.patterns.observe_response(q, ideal, feedback_score=0.8)

        # Simulate LLM down
        class _Down:
            def is_available(self):
                return False
            def generate(self, **kwargs):
                return ""

        being._llm_reasoner = _Down()

        # Pattern layer should now provide direct learned responses
        s1 = being.learner.suggest_response("¿Qué es Python?")
        s2 = being.learner.suggest_response("¿Qué es la memoria?")
        assert s1 is not None and "python" in s1.lower()
        assert s2 is not None and "memoria" in s2.lower()

        # And full interaction should still return meaningful text with LLM down
        r1 = being.interact("¿Qué es Python?")["response"].lower()
        r2 = being.interact("¿Qué es la memoria?")["response"].lower()
        assert len(r1.strip()) > 0
        assert len(r2.strip()) > 0

    print("✅ PASSED")


def test_neural_graph_offline_response():
    """Neural graph should produce non-empty responses with LLM unavailable."""
    print("Testing Neural Graph Offline Response...", end=" ")

    with isolated_being() as being:
        # Build neural associations through interactions + positive feedback
        seeds = [
            "perro animal ladrar amigo",
            "animal vivo comida",
            "python lenguaje programacion",
        ]
        for t in seeds:
            being.interact(t)
            being.give_feedback(0.7)

        class _NoLLM:
            def is_available(self):
                return False
            def generate(self, **kwargs):
                return ""

        being._llm_reasoner = _NoLLM()

        r1 = being.interact("perro")["response"]
        r2 = being.interact("python")["response"]

        assert isinstance(r1, str) and len(r1.strip()) > 0
        assert isinstance(r2, str) and len(r2.strip()) > 0

        stats = being.neural.get_stats()
        assert stats["total_nodes"] > 0
        assert stats["total_synapses"] > 0

    print("✅ PASSED")


def test_neurochemistry_modulates_graph_params():
    """Different neurochemical states should yield different graph params."""
    print("Testing Neurochemistry Modulation...", end=" ")

    with isolated_being() as being:
        base = being.chemistry.get_graph_params()

        being.chemistry.modulate("feedback_positive")
        high_reward = being.chemistry.get_graph_params()

        being.chemistry.modulate("feedback_negative")
        stressed = being.chemistry.get_graph_params()

        # At least one core param should differ across states
        assert base != high_reward or high_reward != stressed

    print("✅ PASSED")

def test_persistence():
    """Test that state persists across sessions."""
    print("Testing Persistence...", end=" ")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_persist.db"

        # Session 1: Create memories
        memory1 = MemorySystem(db_path=db_path)
        memory1.remember("remember this", "okay I will", emotion="curiosidad")
        memory1.semantic.learn_concept("persistence", "Surviving across sessions")
        memory1.save_state("user_name", "TestUser")
        memory1.close()

        # Session 2: Verify memories survive
        memory2 = MemorySystem(db_path=db_path)
        assert memory2.episodic.count() >= 1
        assert memory2.semantic.get_concept("persistence") is not None
        assert memory2.load_state("user_name") == "TestUser"

        # Verify recall works
        results = memory2.recall("remember")
        assert len(results["episodic"]) > 0
        memory2.close()

    print("✅ PASSED")


def main():
    print("=" * 50)
    print("🧪 Franquenstein Integration Tests")
    print("=" * 50)
    print()

    tests = [
        test_working_memory,
        test_memory_system,
        test_pattern_detection,
        test_being_interaction,
        test_growth_system,
        test_llm_fallback_stability,
        test_document_reader_txt_md,
        test_fetch_web_text_local_file_url,
        test_learn_command_pipeline_local_text,
        test_curiosity_step_generates_episode,
        test_curiosity_throttling_guardrails,
        test_auto_backup_utility,
        test_offline_response_patterns,
        test_neural_graph_offline_response,
        test_neurochemistry_modulates_graph_params,
        test_persistence,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed.")
    print("=" * 50)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
