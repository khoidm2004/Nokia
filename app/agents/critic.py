from __future__ import annotations

from app.agents.llm import CRITIC_MODEL, call_tool, load_prompt
from app.state import GraphState

CRITIC_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "needs_revision": {
            "type": "boolean",
            "description": "True only if the draft has a clear, named defect that one more extraction pass would fix.",
        },
        "warnings": {
            "type": "array",
            "description": "At most 5 short, specific notes for the human tester.",
            "items": {"type": "string"},
        },
    },
    "required": ["needs_revision", "warnings"],
}


def critic_agent(state: GraphState) -> dict:
    features = state["features"]
    relationships = state["relationships"]

    features_block = "Features:\n" + "\n".join(
        f"{f.id} | {f.name} | {f.category} | {f.description}" for f in features
    )
    if relationships:
        rel_block = "\n".join(
            f"{r.source} -> {r.target} [{r.type}]: {r.rationale}" for r in relationships
        )
    else:
        rel_block = "(none)"
    user_content = features_block + "\n\nRelationships:\n" + rel_block

    try:
        payload = call_tool(
            model=CRITIC_MODEL,
            system_prompt=load_prompt("critic_system.txt"),
            user_content=user_content,
            tool_name="report_critique",
            tool_description="Report whether this draft abstraction model needs one more extraction pass.",
            parameters_schema=CRITIC_TOOL_SCHEMA,
            max_completion_tokens=4000,
        )
    except Exception as exc:
        return {
            "needs_revision": False,
            "revision_count": state["revision_count"] + 1,
            "warnings": state["warnings"] + [f"critic: review step failed ({exc}); continuing without it."],
        }

    new_warnings = [f"critic: {w}" for w in payload.get("warnings", [])][:5]
    return {
        "needs_revision": bool(payload.get("needs_revision", False)),
        "revision_count": state["revision_count"] + 1,
        "warnings": state["warnings"] + new_warnings,
    }
