import streamlit as st
from client.view import call
from dashboard import dashboard

runtime = call("GET", "/api/v1/settings")
workspace = [
    st.Page(dashboard, title="Overview", icon=":material/home:", default=True),
    st.Page("pages/1_Candidate_Profile.py", title="Your profile", icon=":material/person:"),
    st.Page("pages/2_Job_Discovery.py", title="Opportunities", icon=":material/work:"),
    st.Page("pages/3_Job_Match.py", title="Match insights", icon=":material/insights:"),
    st.Page("pages/4_Resume_Studio.py", title="Resume studio", icon=":material/description:"),
    st.Page("pages/5_Applications.py", title="Application tracker", icon=":material/view_kanban:"),
    st.Page("pages/6_Market_Insights.py", title="Skills landscape", icon=":material/bar_chart:"),
    st.Page("pages/9_Settings.py", title="Privacy & session", icon=":material/shield:"),
]
nav = {"Your workspace": workspace}
if not runtime["public_site"]:
    nav["Project details"] = [
        st.Page("pages/7_Developer_Trace.py"),
        st.Page("pages/8_Architecture.py"),
    ]
st.navigation(nav).run()
