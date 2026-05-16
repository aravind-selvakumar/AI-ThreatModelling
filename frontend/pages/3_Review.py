import streamlit as st

from utils.api_client import list_threat_models

st.set_page_config(page_title="Review - ThreatModellingEngine", page_icon="🛡️", layout="wide")

if "token" not in st.session_state:
    st.switch_page("app.py")

st.title("Review Threat Models")

models = list_threat_models(st.session_state.token)

if models:
    for m in models:
        with st.container(border=True):
            cols = st.columns([3, 1, 1, 1])
            cols[0].write(f"**{m['name']}**")
            cols[1].write(f"Status: `{m['status']}`")
            cols[2].write(m["created_at"][:10])
            cols[3].button("View Details", key=f"view_{m['id']}")
else:
    st.info("No threat models to review.")

st.divider()

if st.button("← Back to Dashboard"):
    st.switch_page("pages/1_Dashboard.py")
