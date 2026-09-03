import streamlit as st
from client.design import setup

setup("Developer workspace", "Workflow observability and implementation status.")
st.info(
    "Persistent execution traces are not implemented. "
    "The API calls deterministic services; graph definitions are tested separately. "
    "No live trace is available."
)
