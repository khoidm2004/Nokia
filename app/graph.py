from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.critic import critic_agent
from app.agents.extractor import extractor_agent
from app.agents.relationship_mapper import relationship_agent
from app.nodes.assemble import assemble_model_node
from app.nodes.consistency_check import consistency_check_node
from app.nodes.ingest import ingest_node
from app.nodes.render import render_html_node
from app.state import GraphState


def build_graph() -> StateGraph:
    graph = StateGraph(GraphState)
    graph.add_node("ingest", ingest_node)
    graph.add_node("extract_features", extractor_agent)
    graph.add_node("map_relationships", relationship_agent)
    graph.add_node("critique", critic_agent)
    graph.add_node("consistency_check", consistency_check_node)
    graph.add_node("assemble_model", assemble_model_node)
    graph.add_node("render_html", render_html_node)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "extract_features")
    graph.add_edge("extract_features", "map_relationships")
    graph.add_edge("map_relationships", "critique")
    graph.add_conditional_edges(
        "critique",
        lambda s: "revise" if (s["needs_revision"] and s["revision_count"] < 1) else "proceed",
        {"revise": "extract_features", "proceed": "consistency_check"},
    )
    graph.add_edge("consistency_check", "assemble_model")
    graph.add_edge("assemble_model", "render_html")
    graph.add_edge("render_html", END)
    return graph


def compile_graph():
    return build_graph().compile()


def initial_state(file_path: str, html_path: str) -> GraphState:
    return {
        "file_path": file_path,
        "raw_text": "",
        "lines": [],
        "features": [],
        "relationships": [],
        "warnings": [],
        "needs_revision": False,
        "revision_count": 0,
        "model": None,
        "html_path": html_path,
    }
