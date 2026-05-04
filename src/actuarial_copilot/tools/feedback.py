"""Feedback recording capability for agent learning."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .common import ensure_dir, safe_name


def record_feedback(message: str, topic: str = "general", feedback_dir: str = "agent_feedback") -> dict:
    """Persist user feedback and append it to the lessons log."""
    root = ensure_dir(Path(feedback_dir).resolve())
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = root / f"{timestamp}_{safe_name(topic)}.md"
    path.write_text(
        f"# Agent Feedback: {topic}\n\nRecorded: {timestamp}\n\n## Feedback\n\n{message.strip()}\n",
        encoding="utf-8",
    )
    lessons = root / "LESSONS.md"
    with lessons.open("a", encoding="utf-8") as fh:
        fh.write(f"\n## {timestamp} | {topic}\n\n{message.strip()}\n")
    return {"path": str(path), "lessons": str(lessons), "status": "recorded"}
