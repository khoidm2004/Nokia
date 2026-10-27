from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.schemas import AbstractionModel
from app.state import GraphState


def dedupe_preserving_order(items: list[str]) -> list[str]:
    """Drop exact-duplicate warning strings (the critic may run twice)."""
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def json_path_for(html_path: str) -> Path:
    return Path(html_path).with_suffix(".json")


def assemble_model_node(state: GraphState) -> dict:
    model = AbstractionModel(
        document=Path(state["file_path"]).name,
        generated_at=datetime.now(timezone.utc),
        features=state["features"],
        relationships=state["relationships"],
        warnings=dedupe_preserving_order(state["warnings"]),
    )
    out_json = json_path_for(state["html_path"])
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps(model.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )
    return {"model": model}
