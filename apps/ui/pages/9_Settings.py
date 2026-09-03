import streamlit as st
from client.design import setup
from client.view import call

setup(
    "Privacy & your session",
    "A private workspace to explore your next career move. No account required.",
)
settings = st.session_state["runtime"]
st.subheader("Your data, your choice")
st.write(
    "Your uploaded file is processed in memory. Resume text is sent to Google Gemini only "
    "after you consent. Review every extracted fact before using it."
)
st.write(
    f"Imported jobs and application records expire after {settings['retention_hours']} hours. "
    "Expired records are hidden immediately and removed by scheduled maintenance. "
    "Your profile and resume previews stay in this browser session; save your downloads "
    "before leaving. A new browser session starts a new workspace."
)
st.caption(
    "Workspace identifiers are random. They are not accounts and cannot recover lost sessions."
)
if settings["public_site"]:
    st.info(
        f"This portfolio allows up to {settings['visitor_ai_limit']} AI requests "
        "per visitor per UTC day, subject to a site-wide limit."
    )
else:
    with st.expander("Local configuration"):
        st.write("Mode:", settings["mode"])
        st.write("Model:", settings["model"])
        st.write("Key configured:", settings["gemini_key_configured"])
        st.caption("Change backend values in .env and restart the API. Never share your key.")
        if st.button("Test Gemini connection"):
            with st.spinner("Checking connection…"):
                result = call("POST", "/api/v1/settings/check-gemini")
            if result["ok"]:
                st.success("Gemini is connected.")
            else:
                st.warning("Connection did not return the expected response.")
st.divider()
st.subheader("Clear your workspace")
st.write(
    "Remove this session's imported jobs and application records, and discard its "
    "profile and resume previews."
)
confirmed = st.checkbox("I understand this clears my current workspace")
if st.button("Clear my data", disabled=not confirmed, type="primary"):
    call("DELETE", "/api/v1/workspace")
    for key in list(st.session_state):
        if key != "_workspace_id":
            del st.session_state[key]
    st.success("Your workspace data has been cleared.")
    st.stop()
st.caption(
    "Clearing data does not reset usage limits. Provider-side retention follows "
    "Google's applicable API terms."
)
