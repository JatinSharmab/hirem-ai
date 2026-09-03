import streamlit as st
from client.design import setup, tags
from client.view import call

setup(
    "Your evidence profile",
    "Turn your experience into reviewed facts you can confidently use.",
    "01 / PROFILE",
)
left, right = st.columns([2, 1])
with right:
    if st.session_state["runtime"]["mode"] == "live":
        st.info("Live mode uses Gemini. Upload your own resume and review every extracted fact.")
        st.page_link(
            "pages/9_Settings.py",
            label="Privacy & data handling"
            if st.session_state["runtime"]["public_site"]
            else "Check Gemini setup",
        )
    else:
        with st.container(border=True):
            st.subheader("Start with a demo")
            st.write("Meet a fictional AI engineer and explore the workflow.")
            if st.button("Try Demo Candidate", type="primary", width="stretch"):
                st.session_state["candidate"] = call("POST", "/api/v1/profile/demo")
                st.session_state.pop("fact_review", None)
                st.rerun()
with left:
    with st.container(border=True):
        st.subheader("Bring your own resume")
        upload = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"])
        live = st.session_state["runtime"]["mode"] == "live"
        consent = (
            st.checkbox("I agree to send this resume text to Google Gemini") if live else False
        )
        if st.button("Extract profile", disabled=upload is None or (live and not consent)):
            with st.spinner("Reading your resume…"):
                st.session_state["candidate"] = call(
                    "POST",
                    "/api/v1/profile/parse",
                    files={"file": (upload.name, upload.getvalue())},
                    params={"consent": consent},
                )
            st.session_state.pop("fact_review", None)
            st.rerun()
        st.caption("Confirm every fact before use. Gemini can make extraction mistakes.")
if "candidate" in st.session_state:
    candidate = st.session_state["candidate"]
    st.divider()
    st.subheader(candidate["name"])
    st.write(candidate["summary"])
    with st.expander("Review profile details", expanded=True):
        candidate["name"] = st.text_input("Your name", candidate["name"])
        candidate["experience_years"] = st.number_input(
            "Years of relevant experience",
            min_value=0.0,
            max_value=80.0,
            value=float(candidate["experience_years"]),
            step=0.5,
        )
        places = st.text_input(
            "Preferred locations (comma separated)", ", ".join(candidate["locations"])
        )
        candidate["locations"] = [v.strip() for v in places.split(",") if v.strip()]
    facts = candidate["facts"]
    reviewed_count = sum(f["verified_by_user"] for f in facts)
    a, b, c = st.columns(3)
    a.metric("Extracted facts", len(facts))
    b.metric("Reviewed", reviewed_count)
    c.metric("Awaiting review", len(facts) - reviewed_count)
    st.progress(reviewed_count / max(1, len(facts)), text="Evidence review progress")
    tags(candidate["skills"])
    st.write("")
    overview, ledger = st.tabs(["Review your facts", "How evidence works"])
    with overview:
        st.caption("Tick only facts you can support. Your changes apply when you save.")
        reviewed = st.data_editor(
            facts,
            disabled=[k for k in facts[0] if k != "verified_by_user"] if facts else True,
            column_order=["verified_by_user", "value", "source_text", "category", "id"],
            column_config={
                "verified_by_user": st.column_config.CheckboxColumn("Confirmed"),
                "value": "Skill / fact",
                "source_text": "Source evidence",
                "category": "Type",
                "id": "Fact ID",
            },
            hide_index=True,
            width="stretch",
            key="fact_review",
        )
        if st.button("Save reviewed facts", type="primary"):
            candidate["facts"] = reviewed
            st.toast("Evidence review saved", icon="✓")
            st.rerun()
    with ledger:
        st.write(
            "Matching uses reviewed evidence. Unreviewed facts cannot enter verified resume output."
        )
        st.write(
            "Review confirms your input; it does not independently verify real-world experience."
        )
    st.page_link("pages/2_Job_Discovery.py", label="Continue to opportunities →")
