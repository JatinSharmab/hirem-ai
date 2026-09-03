from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from hireme_ai.workflows.states import ApplicationState


def _prepare(state: ApplicationState) -> ApplicationState:
    return {"package_ready": True, "next_action": "AWAIT_HUMAN_APPROVAL"}


def _approval_gate(state: ApplicationState) -> ApplicationState:
    return {
        "next_action": "OPEN_OFFICIAL_APPLICATION"
        if state.get("approved")
        else "AWAIT_HUMAN_APPROVAL"
    }


def build_application_graph() -> CompiledStateGraph:
    graph = StateGraph(ApplicationState)
    graph.add_node("prepare_package", _prepare)
    graph.add_node("human_approval_gate", _approval_gate)
    graph.set_entry_point("prepare_package")
    graph.add_edge("prepare_package", "human_approval_gate")
    graph.add_edge("human_approval_gate", END)
    return graph.compile()
