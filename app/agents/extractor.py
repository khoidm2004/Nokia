from __future__ import annotations

from app.agents.llm import EXTRACTOR_MODEL, call_tool, load_prompt
from app.nodes.ingest import number_lines
from app.schemas import Feature
from app.state import GraphState

EXTRACT_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "features": {
            "type": "array",
            "description": "Every distinct feature or requirement stated in the document, in document order.",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Sequential id: F1, F2, F3, ..."},
                    "name": {"type": "string", "description": "Short noun phrase, 2-6 words."},
                    "description": {"type": "string", "description": "Exactly one sentence."},
                    "category": {
                        "type": "string",
                        "enum": ["functional", "non_functional", "constraint"],
                    },
                    "start_line": {"type": "integer", "description": "1-based first line that states this feature."},
                    "end_line": {"type": "integer", "description": "1-based last line that states this feature."},
                },
                "required": ["id", "name", "description", "category", "start_line", "end_line"],
            },
        }
    },
    "required": ["features"],
}


def extractor_agent(state: GraphState) -> dict:
    lines = state["lines"]
    n_lines = len(lines)
    user_parts = [
        "Numbered specification document:",
        "",
        number_lines(lines),
    ]
    if state["revision_count"] > 0 and state["warnings"]:
        user_parts += [
            "",
            "A reviewer found these problems with your previous attempt. "
            "Fix them in this pass:",
        ] + [f"- {w}" for w in state["warnings"]]
    user_content = "\n".join(user_parts)

    payload = call_tool(
        model=EXTRACTOR_MODEL,
        system_prompt=load_prompt("extractor_system.txt"),
        user_content=user_content,
        tool_name="extract_features",
        tool_description="Record every feature or requirement found in the specification.",
        parameters_schema=EXTRACT_TOOL_SCHEMA,
        max_completion_tokens=8000,
    )

    features: list[Feature] = []
    warnings: list[str] = []
    for i, raw in enumerate(payload.get("features", []), start=1):
        try:
            start = max(1, min(int(raw["start_line"]), n_lines))
            end = max(start, min(int(raw["end_line"]), n_lines))
            features.append(
                Feature(
                    id=str(raw["id"]).strip() or f"F{i}",
                    name=str(raw["name"]).strip(),
                    description=str(raw["description"]).strip(),
                    category=raw["category"],
                    source_lines=(start, end),
                )
            )
        except Exception as exc:
            warnings.append(f"extractor: dropped malformed feature #{i} ({exc}).")

    if not features:
        raise RuntimeError("Extractor returned no usable features; aborting.")

    return {"features": features, "relationships": [],
            "warnings": state["warnings"] + warnings}
