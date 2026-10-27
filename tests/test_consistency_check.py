from __future__ import annotations

from app.nodes.consistency_check import (
    consistency_check_node,
    dedupe_features,
    dedupe_relationships,
    drop_dangling_edges,
    find_orphans,
    run_consistency_checks,
)
from app.schemas import Feature, Relationship


def _feature(fid, name="X", category="functional", lines=(1, 2)):
    return Feature(id=fid, name=name, description="d", category=category, source_lines=lines)


def test_dedupe_features_keeps_first():
    feats = [
        _feature("F1", name="First"),
        _feature("F1", name="Second"),
    ]
    kept, warnings = dedupe_features(feats)
    assert len(kept) == 1
    assert kept[0].name == "First"
    assert len(warnings) == 1
    assert "duplicate feature id 'F1'" in warnings[0]


def test_dedupe_relationships_keeps_first():
    rels = [
        Relationship(source="F2", target="F1", type="depends_on", rationale="first"),
        Relationship(source="F2", target="F1", type="depends_on", rationale="second"),
    ]
    kept, warnings = dedupe_relationships(rels)
    assert len(kept) == 1
    assert kept[0].rationale == "first"
    assert len(warnings) == 1
    assert "dropped duplicate relationship F2 -> F1 [depends_on]" in warnings[0]


def test_dedupe_relationships_keeps_different_types():
    rels = [
        Relationship(source="F2", target="F1", type="depends_on", rationale="a"),
        Relationship(source="F2", target="F1", type="triggers", rationale="b"),
    ]
    kept, warnings = dedupe_relationships(rels)
    assert len(kept) == 2
    assert warnings == []


def test_drop_dangling_edges_unknown_target():
    feats = [_feature("F1")]
    rels = [Relationship(source="F1", target="F99", type="depends_on", rationale="r")]
    kept, warnings = drop_dangling_edges(feats, rels)
    assert kept == []
    assert len(warnings) == 1
    assert "unknown feature id" in warnings[0]


def test_drop_dangling_edges_unknown_source():
    feats = [_feature("F1")]
    rels = [Relationship(source="F99", target="F1", type="depends_on", rationale="r")]
    kept, warnings = drop_dangling_edges(feats, rels)
    assert kept == []
    assert len(warnings) == 1
    assert "unknown feature id" in warnings[0]


def test_drop_self_edges():
    feats = [_feature("F1")]
    rels = [Relationship(source="F1", target="F1", type="depends_on", rationale="r")]
    kept, warnings = drop_dangling_edges(feats, rels)
    assert kept == []
    assert len(warnings) == 1
    assert "self-relationship on F1" in warnings[0]


def test_drop_dangling_keeps_valid_edges(sample_features, sample_relationships):
    kept, warnings = drop_dangling_edges(sample_features, sample_relationships)
    assert len(kept) == len(sample_relationships)
    assert warnings == []


def test_find_orphans(sample_features, sample_relationships):
    warnings = find_orphans(sample_features, sample_relationships)
    assert len(warnings) == 1
    assert "F4" in warnings[0]


def test_run_consistency_checks_pipeline():
    feats = [
        _feature("F1"),
        _feature("F1", name="dup"),  # duplicate feature id
        _feature("F2"),
        _feature("F3"),  # will become orphan
    ]
    rels = [
        Relationship(source="F1", target="F2", type="depends_on", rationale="a"),
        Relationship(source="F1", target="F2", type="depends_on", rationale="dup"),  # duplicate edge
        Relationship(source="F1", target="F99", type="triggers", rationale="dangling"),  # dangling
    ]
    feats_out, rels_out, warnings = run_consistency_checks(feats, rels)
    assert len(feats_out) == 3  # F1, F2, F3 (duplicate F1 dropped)
    assert len(rels_out) == 1  # only F1 -> F2 depends_on survives
    assert len(warnings) == 4


def test_consistency_check_node_appends_to_existing_warnings(sample_features, sample_relationships):
    state = {
        "features": sample_features,
        "relationships": sample_relationships,
        "warnings": ["pre-existing"],
    }
    result = consistency_check_node(state)
    assert result["warnings"][0] == "pre-existing"
    assert len(result["warnings"]) > 1
