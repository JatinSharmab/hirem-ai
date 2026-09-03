from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from hireme_ai.workflows.states import DiscoveryState


def _plan(state: DiscoveryState) -> DiscoveryState:
    return {"warnings": [] if state.get("query") else ["Empty search query"]}


def _normalize(state: DiscoveryState) -> DiscoveryState:
    return {"jobs": state.get("jobs", [])}


def build_discovery_graph() -> CompiledStateGraph:
    graph = StateGraph(DiscoveryState)
    graph.add_node("search_planner", _plan)
    graph.add_node("normalize_deduplicate", _normalize)
    graph.set_entry_point("search_planner")
    graph.add_edge("search_planner", "normalize_deduplicate")
    graph.add_edge("normalize_deduplicate", END)
    return graph.compile()
