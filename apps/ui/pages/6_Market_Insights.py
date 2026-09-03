import streamlit as st
from client.design import setup
from client.view import call

setup(
    "Explore the skills landscape",
    "See which skills appear in the opportunities in this workspace.",
    "INSIGHTS",
)
st.caption("Keyword counts in your imported corpus; not a broad market survey.")
skills = call("GET", "/api/v1/insights/skills")["skills"]
jobs = call("GET", "/api/v1/jobs")
a, b, c = st.columns(3)
a.metric("Roles analyzed", len(jobs))
b.metric("Distinct skill mentions", len(skills))
c.metric("Locations", len({j["location"] for j in jobs}))
if not skills:
    st.info("Import jobs to explore skill mentions.")
    st.stop()
chart, table = st.tabs(["Skill demand", "Explore data"])
with chart:
    count = st.slider("Skills to display", 1, max(2, len(skills)), min(8, max(2, len(skills))))
    chosen = skills[:count]
    st.bar_chart({s["skill"]: s["job_count"] for s in chosen}, horizontal=True, color="#087F72")
with table:
    search = st.text_input("Filter skills", placeholder="Search a skill")
    st.dataframe(
        [s for s in skills if search.lower() in s["skill"].lower()],
        hide_index=True,
        width="stretch",
    )
