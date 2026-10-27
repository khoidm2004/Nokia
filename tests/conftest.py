from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.schemas import AbstractionModel, Feature, Relationship


@pytest.fixture
def sample_features() -> list[Feature]:
    return [
        Feature(id="F1", name="Operator Sign-In", description="Operators sign in with email and password.",
                category="functional", source_lines=(9, 12)),
        Feature(id="F2", name="Vehicle Registration", description="An operator registers a vehicle by VIN.",
                category="functional", source_lines=(14, 17)),
        Feature(id="F3", name="Live Location Tracking", description="The platform shows vehicle positions on a map.",
                category="functional", source_lines=(19, 22)),
        Feature(id="F4", name="Data Retention Policy", description="Positions are kept for 90 days.",
                category="constraint", source_lines=(40, 42)),
    ]


@pytest.fixture
def sample_relationships() -> list[Relationship]:
    return [
        Relationship(source="F2", target="F1", type="depends_on",
                     rationale="Registration requires a signed-in operator."),
        Relationship(source="F3", target="F2", type="depends_on",
                     rationale="Tracking only starts once a vehicle is registered."),
    ]


@pytest.fixture
def sample_model(sample_features, sample_relationships) -> AbstractionModel:
    return AbstractionModel(
        document="sample_spec.txt",
        generated_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        features=sample_features,
        relationships=sample_relationships,
        warnings=["consistency: feature F4 has no relationships (orphan)."],
    )
