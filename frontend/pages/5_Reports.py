import streamlit as st

st.set_page_config(page_title="Reports - ThreatModellingEngine", page_icon="🛡️", layout="wide")

if "token" not in st.session_state:
    st.switch_page("app.py")

st.title("📄 Export Reports")

st.info("Export threat model results as PDF reports. Select a model and export format.")

st.selectbox("Select Threat Model", ["— No models available yet —"])

col1, col2 = st.columns(2)
col1.selectbox("Export Format", ["PDF"], disabled=True)
col2.selectbox("Include", ["Threats Only", "Full Report (with mitigations)", "Executive Summary"])

st.divider()

if st.button("Export PDF", type="primary", use_container_width=True, disabled=True):
    st.info("Export will be available after threat analysis is implemented.")

st.divider()

if st.button("← Back to Dashboard"):
    st.switch_page("pages/1_Dashboard.py")
