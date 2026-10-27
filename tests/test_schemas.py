from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from app.schemas import EDGE_TYPES, AbstractionModel, Feature, Relationship


def test_feature_round_trip():
    f = Feature(
        id="F1",
        name="Operator Sign-In",
        description="Operators sign in with email and password.",
        category="functional",
        source_lines=(1, 3),
    )
    f2 = Feature.model_validate_json(f.model_dump_json())
    assert f2 == f
    assert f2.source_lines == (1, 3)
    assert isinstance(f2.source_lines, tuple)


def test_feature_rejects_unknown_category():
    with pytest.raises(ValidationError):
        Feature(
            id="F1",
            name="X",
            description="Y",
            category="nonsense",
            source_lines=(1, 2),
        )


def test_relationship_rejects_unknown_type():
    with pytest.raises(ValidationError):
        Relationship(source="F1", target="F2", type="causes", rationale="r")


def test_all_five_edge_types_accepted():
    assert len(EDGE_TYPES) == 5
    assert set(EDGE_TYPES) == {
        "depends_on", "triggers", "excludes", "shares_data", "part_of",
    }
    for t in EDGE_TYPES:
        Relationship(source="F1", target="F2", type=t, rationale="r")


def test_abstraction_model_round_trip(sample_model):
    assert AbstractionModel.model_validate_json(sample_model.model_dump_json()) == sample_model


def test_abstraction_model_json_mode_is_serialisable(sample_model):
    data = sample_model.model_dump(mode="json")
    json.dumps(data)
    assert data["features"][0]["source_lines"] == [9, 12]
    assert isinstance(data["generated_at"], str)
