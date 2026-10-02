import os

import httpx
import streamlit as st
from client.api import HireMeAPI, ServiceUnavailableError

UNAVAILABLE_MESSAGE = (
    "The service is starting or temporarily unavailable. "
    "On free hosting, the first visit after inactivity can take about a minute. "
    "Please wait a moment, then reload this page."
)


def call(method: str, path: str, **kwargs):
    try:
        return HireMeAPI().request(method, path, **kwargs)
    except httpx.HTTPStatusError as exc:
        fallback = (
            UNAVAILABLE_MESSAGE
            if exc.response.status_code in (502, 503, 504)
            else "The request could not be completed. Please check your input."
        )
        try:
            body = exc.response.json()
            detail = body.get("detail") if isinstance(body, dict) else None
            if not isinstance(detail, str):
                detail = fallback
        except ValueError:
            detail = fallback
        st.error(f"{detail} (HTTP {exc.response.status_code})")
    except ServiceUnavailableError:
        st.warning(UNAVAILABLE_MESSAGE)
    except httpx.RequestError:
        if os.getenv("APP_ENV") == "production":
            st.warning(UNAVAILABLE_MESSAGE)
        else:
            st.error("Cannot reach the API. Start the backend on port 8000 and try again.")
    except ValueError:
        st.error("The service configuration needs attention. Please contact the site owner.")
    if st.button("Reload page", key="reload_after_api_error"):
        st.rerun()
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
