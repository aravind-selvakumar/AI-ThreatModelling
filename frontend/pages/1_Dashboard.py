import streamlit as st

from utils.api_client import list_threat_models

st.set_page_config(page_title="Dashboard - ThreatModellingEngine", page_icon="🛡️", layout="wide")

if "token" not in st.session_state:
    st.switch_page("app.py")

token = st.session_state.token
role = st.session_state.get("role", "guest")

st.title("Dashboard")
st.markdown("---")

col1, col2, col3 = st.columns(3)
col1.metric("Role", role.title())
col2.metric("Username", st.session_state.get("username", "—"))
col3.metric("Status", "Connected")

st.divider()

st.subheader("Recent Threat Models")
models = list_threat_models(token)

if models:
    for m in models:
        with st.container(border=True):
            cols = st.columns([3, 1, 1, 1])
            cols[0].write(f"**{m['name']}**")
            cols[1].write(f"Status: `{m['status']}`")
            cols[2].write(m["created_at"][:10])
            if cols[3].button("Open", key=f"open_{m['id']}"):
                st.switch_page("pages/3_Review.py")
else:
    st.info("No threat models yet. Create one to get started.")

st.divider()

if st.button("➕ New Threat Model", type="primary", use_container_width=True):
    st.switch_page("pages/2_New_Model.py")
