from __future__ import annotations

from app.loaders.txt_loader import TxtLoader
from app.state import GraphState

# Hard guard so an oversized spec fails loudly instead of being silently
# truncated (Architect.md s10). DO NOT tune this value to make a test pass.
MAX_SPEC_CHARS = 40_000


class SpecTooLargeError(ValueError):
    pass


def number_lines(lines: list[str]) -> str:
    """Render lines as '   1: text' for the extractor prompt (1-based)."""
    return "\n".join(f"{i:>4}: {line}" for i, line in enumerate(lines, start=1))


def ingest_node(state: GraphState) -> dict:
    raw_text, lines = TxtLoader().load(state["file_path"])
    if len(raw_text) > MAX_SPEC_CHARS:
        raise SpecTooLargeError(
            f"Spec is {len(raw_text)} characters, which exceeds the "
            f"single-pass limit of {MAX_SPEC_CHARS}. v1 does not chunk; "
            f"split the document and run it in parts."
        )
    if not raw_text.strip():
        raise ValueError(f"Spec file is empty: {state['file_path']}")
    return {"raw_text": raw_text, "lines": lines}
