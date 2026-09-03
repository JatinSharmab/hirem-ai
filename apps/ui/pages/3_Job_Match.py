import copy

import streamlit as st
from client.design import setup, tags
from client.view import call, selection

setup(
    "See the evidence behind your fit",
    "Understand your strengths, your gaps, and what to do next.",
    "03 / MATCH",
)
candidate, job, requirement = selection()
if st.button("Calculate Career Fit Score", type="primary"):
    with st.spinner("Mapping your reviewed evidence…"):
        result = call(
            "POST",
            "/api/v1/matches",
            json={"candidate": candidate, "job": job, "requirement": requirement},
        )
    st.session_state["match_view"] = {
        "job": job["id"],
        "candidate": copy.deepcopy(candidate),
        "result": result,
    }
view = st.session_state.get("match_view")
if view and view["job"] == job["id"] and view["candidate"] == candidate:
    result = view["result"]
    score = result["score"]["total"]
    st.write("")
    a, b, c = st.columns(3)
    a.metric("Career Fit Score", f"{score:.0f}/100")
    b.metric(
        "Supported requirements", sum(bool(e["candidate_fact_ids"]) for e in result["evidence"])
    )
    c.metric("Skill gaps", len(result["gaps"]))
    st.progress(
        score / 100,
        text="Strong coverage"
        if score >= 75
        else "Some alignment"
        if score >= 40
        else "Limited coverage",
    )
    st.caption(
        "Heuristic demo score, not an ATS score. Semantic and responsibility "
        "measures use coverage proxies."
    )
    for warning in result["eligibility_warnings"]:
        st.warning(warning)
    evidence, gaps, breakdown = st.tabs(["Evidence map", "Growth opportunities", "Score breakdown"])
    with evidence:
        for item in result["evidence"]:
            with st.container(border=True):
                st.markdown(
                    f"**{'✓' if item['candidate_fact_ids'] else '○'} {item['requirement']}**"
                )
                if item["evidence"]:
                    st.write(" · ".join(item["evidence"]))
                    st.caption("Evidence: " + ", ".join(item["candidate_fact_ids"]))
                else:
                    st.caption("No reviewed evidence found in your profile.")
    with gaps:
        if not result["gaps"]:
            st.success("Your reviewed facts cover the extracted skills.")
        for gap in result["gaps"]:
            with st.container(border=True):
                st.markdown(f"**{gap['skill']}**")
                tags([gap["priority"].title()])
                st.write(
                    "If you have this experience, add and review its evidence. "
                    "Otherwise, treat it as a learning opportunity."
                )
    with breakdown:
        st.bar_chart(
            {k.replace("_", " ").title(): v for k, v in result["score"].items() if k != "total"},
            horizontal=True,
            color="#087F72",
        )
        with st.expander("Review extracted requirements"):
            st.json(requirement)
    st.page_link("pages/4_Resume_Studio.py", label="Create a verified extract for this role →")
else:
    st.info("Calculate your fit to reveal the evidence map and skill gaps for this role.")
