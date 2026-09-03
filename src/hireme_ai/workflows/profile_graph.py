from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from hireme_ai.profile.extractor import demo_extract_profile
from hireme_ai.profile.redactor import redact_pii
from hireme_ai.workflows.states import ProfileState


def _redact(state: ProfileState) -> ProfileState:
    return {"redacted_text": redact_pii(state.get("raw_text", ""))}


def _extract(state: ProfileState) -> ProfileState:
    profile = demo_extract_profile(state.get("raw_text", ""))
    return {"profile": profile.model_dump()}


def build_profile_graph() -> CompiledStateGraph:
    graph = StateGraph(ProfileState)
    graph.add_node("redact_logs", _redact)
    graph.add_node("extract_profile", _extract)
    graph.set_entry_point("redact_logs")
    graph.add_edge("redact_logs", "extract_profile")
    graph.add_edge("extract_profile", END)
    return graph.compile()
