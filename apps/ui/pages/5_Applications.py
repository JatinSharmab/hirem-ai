import streamlit as st
from client.design import setup, tags
from client.view import call

setup(
    "Keep your next steps in view",
    "A simple pipeline for the opportunities you want to pursue.",
    "05 / TRACK",
)
st.caption(
    "Records belong to this visitor session and expire automatically. Status changes never "
    "submit applications."
)
jobs = call("GET", "/api/v1/jobs")
if not jobs:
    st.info("Import a job on Job Discovery first.")
    st.stop()
job_map = {j["id"]: j for j in jobs}
job = st.selectbox(
    "Add an opportunity", jobs, format_func=lambda j: f"{j['title']} · {j['company']}"
)
if st.button("Track job", type="primary"):
    existing = call("GET", "/api/v1/applications")
    if any(a["job_id"] == job["id"] for a in existing):
        st.toast("This job is already tracked.")
    else:
        call("POST", "/api/v1/applications", params={"job_id": job["id"]})
        st.toast("Added to your pipeline")
records = call("GET", "/api/v1/applications")
a, b, c = st.columns(3)
a.metric("In your pipeline", len(records))
b.metric("Applied", sum(r["status"] == "APPLIED" for r in records))
c.metric("Interviews", sum(r["status"] == "INTERVIEW" for r in records))
statuses = [
    "DISCOVERED",
    "SHORTLISTED",
    "RESUME_READY",
    "READY_TO_APPLY",
    "APPLIED",
    "RECRUITER_RESPONSE",
    "INTERVIEW",
    "OFFER",
    "REJECTED",
    "WITHDRAWN",
]
board, list_tab = st.tabs(["Pipeline board", "Update records"])
with board:
    columns = st.columns(3)
    for col, title, states in [
        (columns[0], "Preparing", statuses[:4]),
        (columns[1], "In progress", statuses[4:7]),
        (columns[2], "Outcome", statuses[7:]),
    ]:
        with col:
            st.subheader(title)
            group = [r for r in records if r["status"] in states]
            if not group:
                st.caption("No opportunities here yet.")
            for record in group:
                j = job_map.get(record["job_id"], {})
                with st.container(border=True):
                    st.markdown(f"**{j.get('title', record['job_id'])}**")
                    st.caption(j.get("company", ""))
                    tags([record["status"].replace("_", " ").title()])
with list_tab:
    if not records:
        st.info("Track an opportunity to start your pipeline.")
    for item in records:
        with st.container(border=True):
            st.markdown(f"**{job_map.get(item['job_id'], {}).get('title', item['job_id'])}**")
            status = st.selectbox(
                "Recorded status",
                statuses,
                key=item["id"],
                index=statuses.index(item["status"]),
                format_func=lambda s: s.replace("_", " ").title(),
            )
            if st.button("Save status", key="save-" + item["id"]):
                call("PATCH", f"/api/v1/applications/{item['id']}", params={"status": status})
                st.toast("Pipeline updated")
                st.rerun()
