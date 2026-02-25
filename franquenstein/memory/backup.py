"""Safety utilities for memory database backups."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil


def auto_backup(db_path: Path, keep_last: int = 5) -> Path:
    """Create a timestamped backup and prune old backups.

    Args:
        db_path: Path to memory.db
        keep_last: Number of latest backups to keep
    """
    db_path = db_path.expanduser().resolve()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = db_path.parent / f"memory_backup_{ts}.db"
    shutil.copy2(db_path, backup)

    backups = sorted(db_path.parent.glob("memory_backup_*.db"))
    for old in backups[:-keep_last]:
        try:
            old.unlink()
        except Exception:
            pass

    return backup
