from __future__ import annotations

from app.agents.llm import RELATIONSHIP_MODEL, call_tool, load_prompt
from app.schemas import Relationship
from app.state import GraphState

RELATIONSHIP_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "relationships": {
            "type": "array",
            "description": "Typed, justified edges between the given features.",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Feature id the edge starts at."},
                    "target": {"type": "string", "description": "Feature id the edge points to."},
                    "type": {
                        "type": "string",
                        "enum": ["depends_on", "triggers", "excludes", "shares_data", "part_of"],
                    },
                    "rationale": {"type": "string", "description": "One sentence justifying this edge."},
                },
                "required": ["source", "target", "type", "rationale"],
            },
        }
    },
    "required": ["relationships"],
}


def relationship_agent(state: GraphState) -> dict:
    features = state["features"]
    user_content = "Features:\n" + "\n".join(
        f"{f.id} | {f.name} | {f.category} | {f.description}" for f in features
    )

    payload = call_tool(
        model=RELATIONSHIP_MODEL,
        system_prompt=load_prompt("relationship_system.txt"),
        user_content=user_content,
        tool_name="map_relationships",
        tool_description="Record the typed relationships between the given features.",
        parameters_schema=RELATIONSHIP_TOOL_SCHEMA,
        max_completion_tokens=6000,
    )

    relationships: list[Relationship] = []
    warnings: list[str] = []
    for i, raw in enumerate(payload.get("relationships", []), start=1):
        try:
            relationships.append(
                Relationship(
                    source=str(raw["source"]).strip(),
                    target=str(raw["target"]).strip(),
                    type=raw["type"],
                    rationale=str(raw["rationale"]).strip(),
                )
            )
        except Exception as exc:
            warnings.append(f"relationship_mapper: dropped malformed relationship #{i} ({exc}).")

    if not relationships:
        warnings.append("relationship_mapper: no relationships were produced.")

    return {"relationships": relationships, "warnings": state["warnings"] + warnings}
