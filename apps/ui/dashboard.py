def dashboard():
    import streamlit as st
    from client.design import hero, setup
    from client.view import call

    setup(
        "Your next move starts here.", "A focused workspace for evidence-backed career decisions."
    )
    hero(
        "Less guesswork. More direction.",
        "Discover opportunities, understand your fit, and build a resume extract "
        "grounded in what you can prove.",
    )
    candidate = st.session_state.get("candidate")
    jobs = call("GET", "/api/v1/jobs")
    cols = st.columns(4)
    cols[0].metric(
        "Opportunities", len(jobs), st.session_state["runtime"]["mode"].title(), delta_color="off"
    )
    cols[1].metric(
        "Reviewed facts", sum(f["verified_by_user"] for f in candidate["facts"]) if candidate else 0
    )
    cols[2].metric("Saved jobs", len(st.session_state.get("saved_jobs", [])))
    cols[3].metric("Resume versions", len(st.session_state.get("versions", [])))
    st.write("")
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Your career workflow")
        for number, title, body, page in [
            (
                "01",
                "Build your evidence profile",
                "Review the facts that power every match and resume.",
                "pages/1_Candidate_Profile.py",
            ),
            (
                "02",
                "Find your fit",
                "Compare opportunities and see exactly where you stand.",
                "pages/2_Job_Discovery.py",
            ),
            (
                "03",
                "Create with confidence",
                "Preview a verified skill extract and export when ready.",
                "pages/4_Resume_Studio.py",
            ),
        ]:
            with st.container(border=True):
                a, b = st.columns([5, 1])
                a.markdown(f"**{number} · {title}**")
                a.caption(body)
                b.page_link(page, label="Open →")
    with right:
        with st.container(border=True):
            if st.session_state["runtime"]["mode"] == "live":
                st.subheader("Your live workspace")
                st.write(
                    "Upload your resume, review its facts, and import the jobs you want to pursue."
                )
                st.page_link("pages/9_Settings.py", label="Privacy & session details")
                st.page_link("pages/1_Candidate_Profile.py", label="Upload your resume")
            else:
                st.subheader("Ready for a test drive?")
                if st.button("Load demo & get started", type="primary", width="stretch"):
                    st.session_state["candidate"] = call("POST", "/api/v1/profile/demo")
                    st.switch_page("pages/1_Candidate_Profile.py")
                st.page_link("pages/9_Settings.py", label="Set up real Gemini")
        st.info("Resume output is a verified skill extract. Full resume rewriting is not enabled.")
