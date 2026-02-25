"""Console Interface — rich terminal UI for interacting with Franquenstein.

Uses the `rich` library for colorful, engaging output that makes
interacting with the being feel alive and dynamic.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich.live import Live
from rich.columns import Columns
from rich import box

from franquenstein.config import BEING_NAME


# ─── Custom Theme ────────────────────────────────────────────

FRANQUENSTEIN_THEME = Theme({
    "being": "bold cyan",
    "user": "bold green",
    "system": "dim yellow",
    "emotion.curiosidad": "bright_blue",
    "emotion.satisfaccion": "bright_green",
    "emotion.confusion": "bright_yellow",
    "emotion.frustracion": "bright_red",
    "emotion.sorpresa": "bright_magenta",
    "emotion.neutral": "white",
    "emotion.alegria": "bright_green",
    "emotion.aburrimiento": "dim white",
    "level": "bold magenta",
    "stat": "cyan",
    "error": "bold red",
    "success": "bold green",
})

# Emotion emoji mapping
EMOTION_ICONS = {
    "curiosidad": "🔍",
    "satisfaccion": "😊",
    "confusion": "🤔",
    "frustracion": "😤",
    "sorpresa": "😲",
    "neutral": "😐",
    "alegria": "😄",
    "aburrimiento": "😑",
}


class ConsoleInterface:
    """Rich terminal interface for Franquenstein.

    Provides a visually engaging console experience with:
    - Colored output by speaker (being vs user)
    - Emotion indicators
    - Level/progress display
    - Special commands (/stats, /memory, /level, /help, /quit)
    """

    def __init__(self):
        self.console = Console(theme=FRANQUENSTEIN_THEME)
        self._show_welcome = True

    # ─── Display Methods ─────────────────────────────────────

    def show_startup(self, level: int, level_name: str, mood: str) -> None:
        """Show the startup banner."""
        emotion_icon = EMOTION_ICONS.get(mood, "😐")

        banner = Text()
        banner.append("╔══════════════════════════════════════════╗\n", style="being")
        banner.append("║  ", style="being")
        banner.append(f"🧠  {BEING_NAME}", style="bold bright_cyan")
        banner.append("  — Digital Being", style="dim cyan")
        banner.append("        ║\n", style="being")
        banner.append("╠══════════════════════════════════════════╣\n", style="being")
        banner.append(f"║  Level: ", style="being")
        banner.append(f"{level} ({level_name})", style="level")
        banner.append(f"   Mood: {emotion_icon} {mood}", style=f"emotion.{mood}")
        spaces = 42 - len(f"  Level: {level} ({level_name})   Mood: {emotion_icon} {mood}")
        banner.append(" " * max(0, spaces) + "║\n", style="being")
        banner.append("╚══════════════════════════════════════════╝\n", style="being")

        self.console.print(banner)

        if level == 0:
            self.console.print(
                "[system]A new digital being awakens... "
                "It knows nothing yet, but is curious about everything.[/]\n"
            )
        else:
            self.console.print(
                f"[system]{BEING_NAME} wakes up and remembers...[/]\n"
            )

    def show_response(self, text: str, emotion: str = "neutral") -> None:
        """Display the being's response with emotion indicator."""
        icon = EMOTION_ICONS.get(emotion, "😐")
        style = f"emotion.{emotion}" if f"emotion.{emotion}" in FRANQUENSTEIN_THEME.styles else "white"

        self.console.print(
            f"  {icon} [being]{BEING_NAME}:[/] [{style}]{text}[/{style}]"
        )

    def show_user_prompt(self) -> str:
        """Show the user input prompt and return their input."""
        self.console.print()
        try:
            user_input = self.console.input("[user]  You:[/] ")
            return user_input.strip()
        except (EOFError, KeyboardInterrupt):
            return "/quit"

    def show_system_message(self, text: str) -> None:
        """Show a system/info message."""
        self.console.print(f"  [system]⚙ {text}[/]")

    def show_level_up(self, old_level: int, new_level: int, old_name: str, new_name: str) -> None:
        """Show a level-up celebration!"""
        self.console.print()
        panel = Panel(
            f"[bold bright_yellow]⭐ LEVEL UP! ⭐[/]\n\n"
            f"[dim]{old_name} (Lv.{old_level})[/]  →  [bold bright_cyan]{new_name} (Lv.{new_level})[/]\n\n"
            f"[bright_green]New capabilities unlocked![/]",
            title="🎉 Growth",
            border_style="bright_yellow",
            box=box.DOUBLE,
            padding=(1, 2),
        )
        self.console.print(panel)

    def show_learning(self, info: dict) -> None:
        """Show brief learning indicators (subtle, not intrusive)."""
        parts = []
        if info.get("new_patterns", 0) > 0:
            parts.append(f"patterns +{info['new_patterns']}")
        if info.get("words_observed", 0) > 0:
            parts.append(f"words +{info['words_observed']}")
        if info.get("consolidated"):
            parts.append(f"consolidated {info['consolidated']}")

        if parts:
            self.console.print(f"  [dim]📖 Learning: {', '.join(parts)}[/]")

    # ─── Special Commands ────────────────────────────────────

    def show_stats(self, memory_stats: dict, learning_stats: dict, growth_status: str) -> None:
        """Show full statistics panel."""
        table = Table(
            title=f"📊 {BEING_NAME} Statistics",
            box=box.ROUNDED,
            border_style="cyan",
        )
        table.add_column("Category", style="bold cyan", width=18)
        table.add_column("Value", style="bright_white")

        # Growth
        table.add_row("Growth", growth_status)
        table.add_section()

        # Memory
        for key, value in memory_stats.items():
            label = key.replace("_", " ").title()
            table.add_row(f"Memory: {label}", str(value))
        table.add_section()

        # Learning
        for key, value in learning_stats.items():
            label = key.replace("_", " ").title()
            table.add_row(f"Learning: {label}", str(value))

        self.console.print()
        self.console.print(table)

    def show_memory(self, recent_episodes: list, known_concepts: list) -> None:
        """Show memory contents."""
        self.console.print()
        self.console.print("[bold cyan]🧠 Memory Contents[/]")
        self.console.print()

        # Recent episodes
        if recent_episodes:
            self.console.print("[bold]Recent Memories:[/]")
            for ep in recent_episodes[:5]:
                icon = EMOTION_ICONS.get(ep.emotion, "😐")
                self.console.print(
                    f"  {icon} [{ep.timestamp[:16]}] "
                    f"[dim]\"{ep.input_text[:40]}\"[/] → "
                    f"[dim]\"{ep.output_text[:40]}\"[/]"
                )
        else:
            self.console.print("  [dim]No memories yet.[/]")

        self.console.print()

        # Known concepts
        if known_concepts:
            self.console.print("[bold]Known Concepts:[/]")
            concept_texts = [
                f"[cyan]{c.concept}[/] ({c.confidence:.0%})"
                for c in known_concepts[:15]
            ]
            self.console.print(f"  {', '.join(concept_texts)}")
        else:
            self.console.print("  [dim]No concepts learned yet.[/]")

    def show_progress(self, progress: dict) -> None:
        """Show growth progress towards next level."""
        self.console.print()
        panel_content = (
            f"[bold]{progress.get('current_name', '?')}[/] "
            f"(Level {progress.get('current_level', 0)})\n\n"
        )
        if progress.get("next_level") is not None:
            panel_content += (
                f"Next: [bright_cyan]{progress.get('next_name', '?')}[/]\n"
                f"📚 Vocabulary: {progress.get('vocabulary', '?')} "
                f"({progress.get('vocab_progress', '?')})\n"
                f"🎯 Experiences: {progress.get('experiences', '?')} "
                f"({progress.get('exp_progress', '?')})"
            )
        else:
            panel_content += "[bright_green]Maximum level reached! 🌟[/]"

        panel = Panel(
            panel_content,
            title="📈 Growth Progress",
            border_style="magenta",
            box=box.ROUNDED,
        )
        self.console.print(panel)

    def show_help(self) -> None:
        """Show available commands."""
        self.console.print()
        table = Table(
            title="Available Commands",
            box=box.SIMPLE,
            border_style="cyan",
        )
        table.add_column("Command", style="bold cyan")
        table.add_column("Description", style="white")

        commands = [
            ("/stats", "Show full statistics"),
            ("/memory", "Show memory contents"),
            ("/level", "Show growth progress"),
            ("/reflect", "Trigger a reflection session"),
            ("/learn <path_or_url>", "Learn from .txt/.md/.pdf or web URL"),
            ("/curious", "Run one proactive curiosity cycle"),
            ("/brain", "Show neural graph stats"),
            ("/chem", "Show neurochemical state"),
            ("/inner", "Show recent inner thoughts"),
            ("/help", "Show this help"),
            ("/quit", "Save and exit"),
        ]
        for cmd, desc in commands:
            table.add_row(cmd, desc)

        self.console.print(table)

    def show_reflection(self, reflections: list) -> None:
        """Show reflection results."""
        self.console.print()
        if reflections:
            self.console.print("[bold cyan]🪞 Reflection Session[/]")
            for r in reflections:
                icon = "💪" if r.category == "strength" else "📝" if r.category == "observation" else "⚠️"
                self.console.print(f"  {icon} {r.insight}")
        else:
            self.console.print("[system]No new insights from this reflection session.[/]")

    def show_goodbye(self, total_experiences: int) -> None:
        """Show exit message."""
        self.console.print()
        self.console.print(
            Panel(
                f"[bright_cyan]{BEING_NAME} goes to sleep...[/]\n"
                f"[dim]Total experiences: {total_experiences}[/]\n"
                f"[dim]All memories saved. See you next time! 💤[/]",
                border_style="cyan",
                box=box.ROUNDED,
            )
        )

    def show_error(self, text: str) -> None:
        """Show an error message."""
        self.console.print(f"  [error]❌ {text}[/]")
