from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.schemas import EDGE_TYPES, AbstractionModel

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "specs" / "sample" / "sample_spec.txt"

requires_groq = pytest.mark.skipif(
    not os.environ.get("GROQ_API_KEY"),
    reason=(
        "GROQ_API_KEY is not set: the end-to-end pipeline has NOT been verified. "
        "Set GROQ_API_KEY to run this test. Set REQUIRE_GROQ=1 to make its absence a failure."
    ),
)


def test_groq_key_present_when_required():
    if os.environ.get("REQUIRE_GROQ") == "1":
        assert os.environ.get("GROQ_API_KEY"), (
            "REQUIRE_GROQ=1 but GROQ_API_KEY is unset: end-to-end verification cannot run."
        )


@pytest.fixture(scope="session")
def cli_run(tmp_path_factory):
    if not os.environ.get("GROQ_API_KEY"):
        pytest.skip(
            "GROQ_API_KEY is not set: the end-to-end pipeline has NOT been verified. "
            "Set GROQ_API_KEY to run this test."
        )
    out_html = tmp_path_factory.mktemp("smoke") / "model.html"
    result = subprocess.run(
        [sys.executable, "-m", "app.main", "--input", str(SPEC), "--output", str(out_html)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=300,
    )
    out_json = out_html.with_suffix(".json")
    model = None
    if out_json.exists():
        model = AbstractionModel.model_validate_json(out_json.read_text(encoding="utf-8"))
    return result, out_html, out_json, model


@requires_groq
def test_cli_exits_zero(cli_run):
    result, _, _, _ = cli_run
    assert result.returncode == 0, result.stderr


@requires_groq
def test_html_file_exists_and_nonempty(cli_run):
    _, html_path, _, _ = cli_run
    assert html_path.exists()
    assert html_path.stat().st_size > 2000


@requires_groq
def test_json_file_parses(cli_run):
    _, _, json_path, model = cli_run
    assert json_path.exists()
    assert model is not None


@requires_groq
def test_feature_count_in_range(cli_run):
    _, _, _, model = cli_run
    assert 5 <= len(model.features) <= 25


@requires_groq
def test_feature_ids_unique(cli_run):
    _, _, _, model = cli_run
    ids = [f.id for f in model.features]
    assert len(set(ids)) == len(ids)


@requires_groq
def test_feature_ids_and_text_nonempty(cli_run):
    _, _, _, model = cli_run
    for f in model.features:
        assert f.id.strip() and " " not in f.id and "\t" not in f.id
        assert f.name.strip()
        assert f.description.strip()


@requires_groq
def test_feature_categories_valid(cli_run):
    _, _, _, model = cli_run
    for f in model.features:
        assert f.category in {"functional", "non_functional", "constraint"}


@requires_groq
def test_feature_source_lines_in_bounds(cli_run):
    _, _, _, model = cli_run
    n_lines = len(SPEC.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n"))
    for f in model.features:
        assert 1 <= f.source_lines[0] <= f.source_lines[1] <= n_lines


@requires_groq
def test_relationships_nonempty(cli_run):
    _, _, _, model = cli_run
    assert len(model.relationships) >= 1


@requires_groq
def test_relationship_endpoints_known(cli_run):
    _, _, _, model = cli_run
    ids = {f.id for f in model.features}
    for r in model.relationships:
        assert r.source in ids
        assert r.target in ids


@requires_groq
def test_relationship_no_self_edges(cli_run):
    _, _, _, model = cli_run
    for r in model.relationships:
        assert r.source != r.target


@requires_groq
def test_relationship_types_and_rationale(cli_run):
    _, _, _, model = cli_run
    for r in model.relationships:
        assert r.type in EDGE_TYPES
        assert r.rationale.strip() != ""


@requires_groq
def test_relationships_no_duplicates(cli_run):
    _, _, _, model = cli_run
    triples = [(r.source, r.target, r.type) for r in model.relationships]
    assert len(set(triples)) == len(triples)


@requires_groq
def test_document_name(cli_run):
    _, _, _, model = cli_run
    assert model.document == "sample_spec.txt"


@requires_groq
def test_html_embedded_json_matches_json_file(cli_run):
    _, html_path, _, model = cli_run
    text = html_path.read_text(encoding="utf-8")
    marker = '<script id="model-data" type="application/json">'
    start = text.index(marker) + len(marker)
    end = text.index("</script>", start)
    data = json.loads(text[start:end])
    assert len(data["features"]) == len(model.features)
    assert len(data["relationships"]) == len(model.relationships)


@requires_groq
def test_html_contains_cdn_and_canvas(cli_run):
    _, html_path, _, _ = cli_run
    text = html_path.read_text(encoding="utf-8")
    assert "https://unpkg.com/cytoscape@3.30.2/dist/cytoscape.min.js" in text
    assert "https://unpkg.com/dagre@0.8.5/dist/dagre.min.js" in text
    assert "https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js" in text
    assert 'id="cy"' in text


@requires_groq
def test_all_feature_ids_appear_in_html(cli_run):
    _, html_path, _, model = cli_run
    text = html_path.read_text(encoding="utf-8")
    for f in model.features:
        assert f.id in text
