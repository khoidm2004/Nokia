from __future__ import annotations

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.schemas import AbstractionModel
from app.state import GraphState

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def embedded_json(model: AbstractionModel) -> str:
    """Serialise the model for an inline <script type="application/json"> block.
    Escaping '<' as \\u003c is valid JSON and makes a literal '</script>' in any
    string impossible, so the blob can never break out of the script tag."""
    return json.dumps(model.model_dump(mode="json"), indent=2).replace("<", "\\u003c")


def render_model_html(model: AbstractionModel, output_path: str | Path) -> Path:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("model.html.j2")
    html = template.render(
        model=model,
        generated_at_str=model.generated_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        feature_count=len(model.features),
        relationship_count=len(model.relationships),
        warning_count=len(model.warnings),
        model_json=embedded_json(model),
    )
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out


def render_html_node(state: GraphState) -> dict:
    model = state["model"]
    if model is None:
        raise RuntimeError("render_html_node called before assemble_model_node.")
    render_model_html(model, state["html_path"])
    return {"html_path": state["html_path"]}
