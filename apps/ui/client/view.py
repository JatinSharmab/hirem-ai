import os

import httpx
import streamlit as st
from client.api import HireMeAPI


def call(method: str, path: str, **kwargs):
    try:
        return HireMeAPI().request(method, path, **kwargs)
    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json().get("detail", "Request failed.")
        except ValueError:
            detail = "The server returned an unreadable error response."
        st.error(f"{detail} (HTTP {exc.response.status_code})")
    except httpx.RequestError:
        if os.getenv("APP_ENV") == "production":
            st.error("The service is waking up or temporarily unavailable. Please retry shortly.")
        else:
            st.error("Cannot reach the API. Start the backend on port 8000 and try again.")
    except ValueError:
        st.error("The service configuration needs attention. Please contact the site owner.")
    st.stop()


def selection():
    if "candidate" not in st.session_state:
        st.info(
            "Your profile is the starting point. Load a candidate to see personalized evidence."
        )
        st.page_link("pages/1_Candidate_Profile.py", label="Build your profile →")
        st.stop()
    jobs = call("GET", "/api/v1/jobs")
    if not jobs:
        st.info("Import a job on Job Discovery first, then analyze it with Gemini.")
        st.page_link("pages/2_Job_Discovery.py", label="Import a job")
        st.stop()
    selected = st.session_state.get("selected_job_id")
    index = next((i for i, j in enumerate(jobs) if j["id"] == selected), 0)
    job = st.selectbox(
        "Target role", jobs, index=index, format_func=lambda j: f"{j['title']} · {j['company']}"
    )
    st.session_state["selected_job_id"] = job["id"]
    requirement = call("GET", f"/api/v1/jobs/{job['id']}/requirements")
    return st.session_state["candidate"], job, requirement
