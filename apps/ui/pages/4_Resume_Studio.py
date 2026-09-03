import base64
import copy
from html import escape

import streamlit as st
from client.design import setup
from client.view import call, selection

setup(
    "Resume Studio",
    "Create, review, and export content grounded in your confirmed facts.",
    "04 / CREATE",
)
candidate, job, requirement = selection()
st.caption(
    "Output is a conservative skill extract, not a complete professional resume. "
    "Versions last this session."
)
live = st.session_state["runtime"]["mode"] == "live"
consent = (
    st.checkbox("Allow Gemini to select relevant content from my reviewed facts") if live else False
)
if st.button("Create verified skill extract", type="primary", disabled=live and not consent):
    with st.spinner("Building and verifying your extract…"):
        version = call(
            "POST",
            "/api/v1/resumes/tailor",
            json={
                "candidate": candidate,
                "requirement": requirement,
                "job_id": job["id"],
                "company": job["company"],
                "consent": consent,
            },
        )
    st.session_state.setdefault("versions", []).append(
        {"version": version, "candidate": copy.deepcopy(candidate)}
    )
    st.toast("New version created")
versions = [
    v
    for v in reversed(st.session_state.get("versions", []))
    if v["version"]["target_job_id"] == job["id"]
]
if not versions:
    st.info("Your preview will appear here. Create an extract to get started.")
else:
    selected = st.selectbox(
        "Version history",
        range(len(versions)),
        format_func=lambda i: (
            f"Version {len(versions) - i} / "
            f"{versions[i]['version']['verification_status']} / "
            f"{versions[i]['version']['id'][:8]}"
        ),
    )
    item = versions[selected]
    version = item["version"]
    left, right = st.columns([2, 1])
    with left:
        bullets = "".join(f"<li>{escape(b['text'])}</li>" for b in version["bullets"])
        st.markdown(
            '<div class="paper"><div class="eyebrow">VERIFIED SKILL EXTRACT</div>'
            f"<h2>{escape(item['candidate']['name'])}</h2>"
            f'<p class="muted">Prepared for {escape(job["title"])} / '
            f"{escape(job['company'])}</p><hr><ul>{bullets}</ul></div>",
            unsafe_allow_html=True,
        )
        with st.expander("Inspect provenance"):
            for bullet in version["bullets"]:
                st.write(bullet["text"])
                st.caption("Source facts: " + ", ".join(bullet["source_fact_ids"]))
                for note in bullet["verifier_notes"]:
                    st.warning(note)
    with right:
        with st.container(border=True):
            st.subheader("Review & export")
            if version["verification_status"] == "PASSED":
                st.success("Factual checks passed")
                st.caption(f"{len(version['bullets'])} statements linked to reviewed facts.")
                if st.checkbox(
                    "I reviewed this extract and approve downloading it", key=version["id"]
                ):
                    for fmt in ("pdf", "docx"):
                        cache = st.session_state.setdefault("export_cache", {})
                        key = f"{version['id']}-{fmt}"
                        if key not in cache:
                            cache[key] = base64.b64decode(
                                call("POST", f"/api/v1/resumes/export/{fmt}", json=item)["content"]
                            )
                        st.download_button(
                            f"Download {fmt.upper()}",
                            cache[key],
                            file_name=f"hireme-{version['id']}.{fmt}",
                            key=key,
                            width="stretch",
                            mime="application/pdf"
                            if fmt == "pdf"
                            else (
                                "application/vnd.openxmlformats-officedocument."
                                "wordprocessingml.document"
                            ),
                        )
            else:
                st.warning(
                    "This extract is not ready for export. Review your facts or "
                    "choose a role with supported skills."
                )
    st.page_link("pages/5_Applications.py", label="Continue to application tracker →")
