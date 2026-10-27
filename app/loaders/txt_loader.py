from __future__ import annotations

from pathlib import Path


class TxtLoader:
    """v1 DocLoader implementation: plain UTF-8 .txt files only."""

    def load(self, path: str) -> tuple[str, list[str]]:
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"Spec file not found: {path}")
        if p.suffix.lower() != ".txt":
            raise ValueError(
                f"Unsupported input type '{p.suffix}'. v1 supports .txt only."
            )
        raw = p.read_text(encoding="utf-8")
        raw = raw.replace("\r\n", "\n").replace("\r", "\n")
        lines = raw.split("\n")
        return raw, lines
