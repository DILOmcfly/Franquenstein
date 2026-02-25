"""Local LLM reasoning module for Franquenstein.

Uses a local Ollama server to generate responses when the being reaches
Level 2+ (child and above). If Ollama is unavailable or fails, callers
must fallback to the native rule-based behavior.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class LocalLLMReasoner:
    """Thin wrapper over Ollama's local HTTP API."""

    def __init__(
        self,
        model: str = "phi3:mini",
        base_url: str = "http://127.0.0.1:11434",
        timeout: float = 20.0,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def is_available(self) -> bool:
        """Return True if Ollama API responds quickly."""
        req = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
        try:
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                return 200 <= resp.status < 300
        except Exception:
            return False

    def generate(
        self,
        *,
        input_text: str,
        level_name: str,
        mood: str,
        working_memory: list[dict[str, Any]],
        known_concepts: list[str],
        good_examples: list[dict[str, str]] | None = None,
        user_name: str = "",
    ) -> str:
        """Generate a concise response grounded in current context."""
        system_prompt = (
            "Eres Franquenstein, un ser digital en crecimiento. "
            "Habla breve, claro y natural. Máximo 2 frases. "
            "No inventes recuerdos. Usa el contexto disponible. "
            "Si no estás seguro, di que sigues aprendiendo."
        )

        context_lines = []
        if user_name:
            context_lines.append(f"Usuario conocido: {user_name}")
        context_lines.append(f"Nivel actual: {level_name}")
        context_lines.append(f"Estado emocional: {mood}")

        if working_memory:
            context_lines.append("Memoria reciente:")
            for item in working_memory[-5:]:
                inp = str(item.get("input_text", "")).strip()
                out = str(item.get("output_text", "")).strip()
                if inp:
                    context_lines.append(f"- Usuario: {inp[:120]}")
                if out:
                    context_lines.append(f"- Franquenstein: {out[:120]}")

        if known_concepts:
            context_lines.append(
                "Conceptos conocidos (muestra): "
                + ", ".join(known_concepts[:30])
            )

        if good_examples:
            context_lines.append("Ejemplos de respuestas previas bien valoradas:")
            for ex in good_examples[:3]:
                inp = ex.get("input", "").strip()
                out = ex.get("output", "").strip()
                if inp and out:
                    context_lines.append(f"- Entrada: {inp[:120]}")
                    context_lines.append(f"- Buena respuesta: {out[:120]}")

        user_prompt = (
            "\n".join(context_lines)
            + "\n\n"
            + f"Entrada actual del usuario: {input_text}\n"
            + "Responde como Franquenstein:"
        )

        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": 0.4,
                "num_predict": 120,
            },
        }

        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Invalid JSON response from Ollama") from exc

        response = str(parsed.get("response", "")).strip()
        if not response:
            raise RuntimeError("Empty response from Ollama")

        return response
