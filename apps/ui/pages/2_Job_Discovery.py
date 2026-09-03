import streamlit as st
from client.design import choose_job, empty, setup, tags
from client.view import call

setup(
    "Discover your next opportunity",
    "Explore roles, save your shortlist, and inspect the evidence behind your fit.",
    "02 / DISCOVER",
)
live = st.session_state["runtime"]["mode"] == "live"
if live:
    with st.expander("Import a real job", expanded=True):
        manual, ats = st.tabs(["Paste job description", "Public ATS board"])
        with manual:
            with st.form("import_jd"):
                title = st.text_input("Job title")
                company = st.text_input("Company")
                location = st.text_input("Location (optional)")
                description = st.text_area("Full job description", height=180)
                if st.form_submit_button("Save job", type="primary"):
                    if not title.strip() or not company.strip() or len(description.strip()) < 50:
                        st.error(
                            "Provide title, company and at least 50 characters of job description."
                        )
                    else:
                        call(
                            "POST",
                            "/api/v1/jobs/import",
                            json={
                                "title": title.strip(),
                                "company": company.strip(),
                                "description": description.strip(),
                                "location": location.strip() or None,
                            },
                        )
                        st.success("Job saved. Analyze it with Gemini below.")
        with ats:
            st.caption("Use the company board slug from its public Greenhouse, Lever or Ashby URL.")
            source = st.selectbox("ATS source", ["greenhouse", "lever", "ashby"])
            board = st.text_input("Company board identifier", placeholder="company-slug")
            keyword = st.text_input("Role keyword (optional)")
            if st.button("Fetch real jobs"):
                with st.spinner("Fetching the public board..."):
                    fetched = call(
                        "POST",
                        "/api/v1/jobs/discover",
                        params={"source": source, "board": board, "query": keyword},
                    )
                st.success(f"Imported {len(fetched)} jobs. Active status remains unverified.")
jobs = call("GET", "/api/v1/jobs")
a, b, c = st.columns([3, 2, 2])
query = a.text_input(
    "Search roles or companies", placeholder="Try AI Engineer, Python, or a company"
)
locations = b.multiselect("Location", sorted({j["location"] for j in jobs if j["location"]}))
mode = c.selectbox("Show", ["All opportunities", "Saved jobs"])
saved = st.session_state.setdefault("saved_jobs", [])
filtered = [
    j
    for j in jobs
    if query.lower() in (j["title"] + " " + j["company"] + " " + j["description"]).lower()
    and (not locations or j["location"] in locations)
    and (mode != "Saved jobs" or j["id"] in saved)
]
st.caption(
    f"{len(filtered)} opportunities / " + ("Imported jobs" if live else "Synthetic fixtures")
)
if not filtered:
    empty(
        "No roles in this view",
        "Try another keyword, clear your location filter, or save a role first.",
    )
for job in filtered:
    with st.container(border=True):
        main, actions = st.columns([4, 1])
        with main:
            st.caption(job["company"].upper())
            st.subheader(job["title"])
            tags(
                [
                    job["location"] or "Location unknown",
                    job["work_mode"] or "Mode unknown",
                    job["source"] if live else "Synthetic role",
                ]
            )
            st.write(job["description"])
        with actions:
            st.write("")
            if live and st.button("Analyze with Gemini", key="analyze-" + job["id"]):
                with st.spinner("Extracting and caching requirements..."):
                    call("POST", f"/api/v1/jobs/{job['id']}/analyze")
                st.success("Analysis saved. Explore fit below.")

            if st.button(
                "Saved ✓" if job["id"] in saved else "Save role",
                key="save-" + job["id"],
                width="stretch",
            ):
                if job["id"] in saved:
                    saved.remove(job["id"])
                else:
                    saved.append(job["id"])
                st.rerun()
            if st.button("Explore fit →", key="fit-" + job["id"], type="primary", width="stretch"):
                choose_job(job["id"], "pages/3_Job_Match.py")
        with st.expander("Source & verification"):
            st.write(job["verification_evidence"])
            st.caption("Active status is unverified." if live else "Status is a synthetic fixture.")
