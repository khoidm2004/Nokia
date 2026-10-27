from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class DocLoader(Protocol):
    def load(self, path: str) -> tuple[str, list[str]]:
        """Return (raw_text, lines) where lines are the 1-indexed source lines."""
        ...
