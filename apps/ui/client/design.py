from html import escape
from pathlib import Path

import streamlit as st
from client.view import call


def setup(title: str, subtitle: str, step: str = "") -> None:
    runtime = call("GET", "/api/v1/settings")
    previous = st.session_state.get("runtime", {}).get("mode")
    if previous and previous != runtime["mode"]:
        for key in [
            "candidate",
            "versions",
            "saved_jobs",
            "match_view",
            "selected_job_id",
            "export_cache",
            "fact_review",
        ]:
            st.session_state.pop(key, None)
    st.session_state["runtime"] = runtime
    st.set_page_config(page_title=f"{title} · HireMe AI", page_icon="✦", layout="wide")
    css = (Path(__file__).resolve().parents[1] / "styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("## ✦ HireMe AI")
        st.caption("YOUR CAREER WORKSPACE")
        st.divider()
        candidate = st.session_state.get("candidate")
        if candidate:
            st.write(candidate["name"].split(" (")[0])
            verified = sum(f["verified_by_user"] for f in candidate["facts"])
            st.caption(f"{verified} reviewed facts · Profile loaded")
        else:
            st.caption("Start by building your evidence profile.")
        st.divider()
        st.caption("YOUR PRIVATE SESSION")
        st.caption("Imported jobs" if runtime["mode"] == "live" else "Synthetic jobs")
    if step:
        st.markdown(f'<div class="eyebrow">{escape(step)}</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)


def tags(values) -> None:
    st.markdown(
        " ".join(f'<span class="tag">{escape(str(v))}</span>' for v in values),
        unsafe_allow_html=True,
    )


def hero(title: str, text: str) -> None:
    st.markdown(
        '<div class="hero"><span class="stage" style="color:#9BDCC8">'
        "BUILD YOUR NEXT CHAPTER</span>"
        f"<h2>{escape(title)}</h2><p>{escape(text)}</p></div>",
        unsafe_allow_html=True,
    )


def empty(title: str, body: str) -> None:
    with st.container(border=True):
        st.subheader(title)
        st.write(body)


def choose_job(job_id: str, page: str) -> None:
    st.session_state["selected_job_id"] = job_id
    st.switch_page(page)
