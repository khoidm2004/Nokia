from __future__ import annotations

import json
from datetime import datetime, timezone

from app.nodes.assemble import assemble_model_node
from app.nodes.render import render_model_html
from app.schemas import AbstractionModel, Feature


def test_render_writes_html(tmp_path, sample_model):
    out = render_model_html(sample_model, tmp_path / "m.html")
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert '<script id="model-data" type="application/json">' in text
    assert "https://unpkg.com/cytoscape@3.30.2/dist/cytoscape.min.js" in text
    assert "https://unpkg.com/dagre@0.8.5/dist/dagre.min.js" in text
    assert "https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js" in text
    assert "Operator Sign-In" in text
    assert "F4" in text
    assert "Warnings (1)" in text
    for edge_type in ("depends_on", "triggers", "excludes", "shares_data", "part_of"):
        assert edge_type in text


def test_embedded_json_parses(tmp_path, sample_model):
    out = render_model_html(sample_model, tmp_path / "m.html")
    text = out.read_text(encoding="utf-8")
    start_marker = '<script id="model-data" type="application/json">'
    start = text.index(start_marker) + len(start_marker)
    end = text.index("</script>", start)
    data = json.loads(text[start:end])
    assert len(data["features"]) == 4
    assert len(data["relationships"]) == 2
    assert data["document"] == "sample_spec.txt"


def test_html_escapes_injected_markup(tmp_path):
    model = AbstractionModel(
        document="evil.txt",
        generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        features=[
            Feature(
                id="F1",
                name='<img src=x onerror="alert(1)">',
                description="d",
                category="functional",
                source_lines=(1, 1),
            )
        ],
        relationships=[],
        warnings=[],
    )
    # inject markup into a feature via relationship-free model is enough, but
    # also test the rationale escape path through an explicit second feature.
    model2 = AbstractionModel(
        document="evil.txt",
        generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        features=[
            Feature(id="F1", name='<img src=x onerror="alert(1)">', description="d",
                     category="functional", source_lines=(1, 1)),
            Feature(id="F2", name="Other", description="d2", category="functional",
                     source_lines=(2, 2)),
        ],
        relationships=[
            {
                "source": "F1",
                "target": "F2",
                "type": "depends_on",
                "rationale": '</script><script>alert(2)</script>',
            }
        ],
        warnings=[],
    )
    out = render_model_html(model2, tmp_path / "m.html")
    text = out.read_text(encoding="utf-8")
    assert "<img src=x" not in text

    start_marker = '<script id="model-data" type="application/json">'
    start = text.index(start_marker) + len(start_marker)
    end = text.index("</script>", start)
    data = json.loads(text[start:end])
    assert len(data["features"]) == 2


def test_sibling_json_written(tmp_path, sample_model):
    state = {
        "file_path": "specs/sample/sample_spec.txt",
        "html_path": str(tmp_path / "m.html"),
        "features": sample_model.features,
        "relationships": sample_model.relationships,
        "warnings": sample_model.warnings,
    }
    assemble_model_node(state)
    json_path = tmp_path / "m.json"
    assert json_path.exists()
    AbstractionModel.model_validate_json(json_path.read_text(encoding="utf-8"))
