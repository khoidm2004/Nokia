from __future__ import annotations

from app.schemas import Feature, Relationship
from app.state import GraphState


def dedupe_features(features: list[Feature]) -> tuple[list[Feature], list[str]]:
    """Keep the first feature per id; warn about each dropped duplicate."""
    seen: set[str] = set()
    kept: list[Feature] = []
    warnings: list[str] = []
    for f in features:
        if f.id in seen:
            warnings.append(f"consistency: dropped duplicate feature id '{f.id}'.")
            continue
        seen.add(f.id)
        kept.append(f)
    return kept, warnings


def dedupe_relationships(
    relationships: list[Relationship],
) -> tuple[list[Relationship], list[str]]:
    """Keep the first edge per (source, target, type); warn about each duplicate."""
    seen: set[tuple[str, str, str]] = set()
    kept: list[Relationship] = []
    warnings: list[str] = []
    for r in relationships:
        key = (r.source, r.target, r.type)
        if key in seen:
            warnings.append(
                f"consistency: dropped duplicate relationship {r.source} -> {r.target} [{r.type}]."
            )
            continue
        seen.add(key)
        kept.append(r)
    return kept, warnings


def drop_dangling_edges(
    features: list[Feature], relationships: list[Relationship]
) -> tuple[list[Relationship], list[str]]:
    """Drop edges whose source or target is not a known feature id, and drop
    self-edges (source == target). Warn once per dropped edge."""
    known_ids = {f.id for f in features}
    kept: list[Relationship] = []
    warnings: list[str] = []
    for r in relationships:
        if r.source == r.target:
            warnings.append(
                f"consistency: dropped self-relationship on {r.source} [{r.type}]."
            )
            continue
        if r.source not in known_ids or r.target not in known_ids:
            warnings.append(
                f"consistency: dropped relationship {r.source} -> {r.target} [{r.type}] (unknown feature id)."
            )
            continue
        kept.append(r)
    return kept, warnings


def find_orphans(
    features: list[Feature], relationships: list[Relationship]
) -> list[str]:
    """Return one warning per feature id that appears in no surviving edge."""
    connected: set[str] = set()
    for r in relationships:
        connected.add(r.source)
        connected.add(r.target)
    warnings: list[str] = []
    for f in features:
        if f.id not in connected:
            warnings.append(f"consistency: feature {f.id} has no relationships (orphan).")
    return warnings


def run_consistency_checks(
    features: list[Feature], relationships: list[Relationship]
) -> tuple[list[Feature], list[Relationship], list[str]]:
    """dedupe_features -> dedupe_relationships -> drop_dangling_edges -> find_orphans,
    in that order, concatenating warnings in that order."""
    feats, w1 = dedupe_features(features)
    rels, w2 = dedupe_relationships(relationships)
    rels, w3 = drop_dangling_edges(feats, rels)
    w4 = find_orphans(feats, rels)
    return feats, rels, w1 + w2 + w3 + w4


def consistency_check_node(state: GraphState) -> dict:
    feats, rels, warns = run_consistency_checks(
        state["features"], state["relationships"]
    )
    return {"features": feats, "relationships": rels,
            "warnings": state["warnings"] + warns}
