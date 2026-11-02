"""Best clear time, kept in a small JSON file."""
import json
from pathlib import Path
from typing import Optional


def load_best_time(path: Path) -> Optional[float]:
    try:
        best = json.loads(path.read_text(encoding="utf-8"))["best_time"]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    if isinstance(best, (int, float)) and best > 0:
        return float(best)
    return None


def save_best_time(path: Path, seconds: float) -> None:
    try:
        path.write_text(json.dumps({"best_time": seconds}), encoding="utf-8")
    except OSError:
        pass  # a read-only install should not stop the game
