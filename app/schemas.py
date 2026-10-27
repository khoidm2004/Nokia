from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

EDGE_TYPES: tuple[str, ...] = (
    "depends_on",
    "triggers",
    "excludes",
    "shares_data",
    "part_of",
)
CATEGORIES: tuple[str, ...] = ("functional", "non_functional", "constraint")


class Feature(BaseModel):
    id: str
    name: str
    description: str
    category: Literal["functional", "non_functional", "constraint"]
    source_lines: tuple[int, int]


class Relationship(BaseModel):
    source: str
    target: str
    type: Literal["depends_on", "triggers", "excludes", "shares_data", "part_of"]
    rationale: str


class AbstractionModel(BaseModel):
    document: str
    generated_at: datetime
    features: list[Feature] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
