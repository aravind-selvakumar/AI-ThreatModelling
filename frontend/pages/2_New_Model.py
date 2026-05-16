import streamlit as st

from utils.api_client import create_threat_model

st.set_page_config(page_title="New Model - ThreatModellingEngine", page_icon="🛡️", layout="wide")

if "token" not in st.session_state:
    st.switch_page("app.py")

st.title("New Threat Model")
st.markdown("Describe the system you want to analyze. You can provide a text description or upload a design sketch.")

input_method = st.radio("Input method", ["Text Description", "Upload Sketch"], horizontal=True)

name = st.text_input("Model Name", placeholder="e.g. Payment Gateway v2")

description = ""
sketch_file = None

if input_method == "Text Description":
    description = st.text_area(
        "System Description",
        placeholder="Describe the system architecture, components, data flows, and trust boundaries...",
        height=200,
    )
else:
    sketch_file = st.file_uploader("Upload architecture sketch/design", type=["png", "jpg", "jpeg"])
    description = st.text_area(
        "Additional context (optional)",
        placeholder="Any extra details about the system...",
        height=100,
    )

st.divider()

with st.expander("📄 Add On-the-Fly Context"):
    st.markdown("Paste design documents, requirements, or any contextual information for this analysis.")
    session_context = st.text_area("Session Context", height=150, placeholder="Paste your design document here...")
    if st.button("Save Context"):
        st.success("Context saved for this session")

st.divider()

col1, col2 = st.columns([1, 4])
if col1.button("Cancel"):
    st.switch_page("pages/1_Dashboard.py")

if col2.button("Create & Analyze", type="primary", use_container_width=True):
    if not name.strip():
        st.error("Model name is required")
    elif input_method == "Text Description" and not description.strip():
        st.error("System description is required")
    else:
        result = create_threat_model(st.session_state.token, name, description)
        if result:
            st.success(f"Threat model '{name}' created!")
            st.switch_page("pages/1_Dashboard.py")
        else:
            st.error("Failed to create threat model")
