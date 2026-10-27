from __future__ import annotations

from typing import TypedDict

from app.schemas import AbstractionModel, Feature, Relationship


class GraphState(TypedDict):
    file_path: str
    raw_text: str
    lines: list[str]
    features: list[Feature]
    relationships: list[Relationship]
    warnings: list[str]
    needs_revision: bool
    revision_count: int
    model: AbstractionModel | None
    html_path: str
