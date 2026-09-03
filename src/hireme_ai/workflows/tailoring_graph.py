from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from hireme_ai.resume.tailoring import deterministic_demo_tailor
from hireme_ai.resume.verifier import verify_resume
from hireme_ai.schemas.candidate import CandidateProfile
from hireme_ai.schemas.job import JobRequirement
from hireme_ai.schemas.resume import GeneratedResumeBullet, VerificationStatus
from hireme_ai.workflows.states import TailoringState


def _generate(state: TailoringState) -> TailoringState:
    candidate = CandidateProfile.model_validate(state["candidate"])
    req = JobRequirement.model_validate(state["requirement"])
    bullets = deterministic_demo_tailor(candidate, req)
    return {"bullets": [b.model_dump() for b in bullets]}


def _verify(state: TailoringState) -> TailoringState:
    candidate = CandidateProfile.model_validate(state["candidate"])
    bullets = [GeneratedResumeBullet.model_validate(b) for b in state.get("bullets", [])]
    checked = verify_resume(bullets, candidate.facts)
    return {
        "bullets": [b.model_dump() for b in checked],
        "verified": bool(checked)
        and all(b.verification_status == VerificationStatus.PASSED for b in checked),
    }


def build_tailoring_graph() -> CompiledStateGraph:
    graph = StateGraph(TailoringState)
    graph.add_node("generate", _generate)
    graph.add_node("deterministic_verify", _verify)
    graph.set_entry_point("generate")
    graph.add_edge("generate", "deterministic_verify")
    graph.add_edge("deterministic_verify", END)
    return graph.compile()
