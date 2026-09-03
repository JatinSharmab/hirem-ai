import streamlit as st
from client.design import setup

setup("Under the hood", "How the current demo connects its components.")
st.markdown("""
**Current demo:** Streamlit → FastAPI → deterministic services → synthetic fixtures.

The repository also contains PostgreSQL models/migrations, Gemini adapters and
LangGraph definitions. These are not yet integrated into a persistent application
workflow. See VALIDATION_REPORT.md for tested capabilities and remaining work.
""")
